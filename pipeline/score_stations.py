"""
Station scores per lead: comparison B (docs/COMPARISONS.md section 2) for raw AIFS ENS,
the bilinear baseline, CERRA and downscaling models, at the 83 scored SYNOP stations.

    python pipeline/score_stations.py --check
    python pipeline/score_stations.py --pred cnn=cnn.npz --out out/ --figure

    import score_stations as SS
    S = SS.load()                                  # load_stage2 + station truth
    F = SS.forecasts(S, {"cnn": "cnn.npz"})
    rows = SS.select_rows(S)                       # dev folds 0-2
    t = SS.score(S, F, rows)                       # long table, one block per lead
    b = SS.bootstrap(S, F, rows, "cnn dressed", "bilinear dressed")

Rows of every table
-------------------
  AIFS ENS          Gaussian N(ens-mean, spread) at the station's nearest 0.25 deg cell
  bilinear          ens-mean interpolated to the CERRA grid (dataset.py B), nearest cell
  <model>           a prediction file, nearest CERRA cell
  CERRA (ceiling)   the analysis at the nearest CERRA cell. Scored here, not truth: its
                    distance from the stations is the floor no downscaling model beats
  <x> dressed       N(x, AIFS spread at the station's 0.25 deg cell), for bilinear, each
                    model and CERRA. A point forecast's CRPS is its absolute error, which
                    loses to any spread by construction; dressing gives every mean the
                    same AIFS spread, so CRPS compares like with like

Columns: n, ME (forecast - obs), RMSE, CRPS (a point row's CRPS is its MAE) and
spread/RMSE = sqrt(mean(s^2) * (M+1)/M) / RMSE with M = 51 members, where s^2 is the
unbiased member variance. The data's spread is the members' np.std (ddof=0,
pipeline/fetch_aifs_overlap.py), so s^2 = sd^2 * M/(M-1) and the ratio is
sqrt(mean(sd^2) * (M+1)/(M-1)) / RMSE: 1 for a reliable ensemble, whose mean misses
by (M+1)/M times the member variance. CRPS uses the spread as stored.

Conventions this file enforces
------------------------------
  * One table per lead, never pooled over leads.
  * Every forecast in a table is scored on identical (station, valid, lead) rows. A
    model file that does not cover the rows is refused unless intersect=True, which
    shrinks every forecast to the rows they all cover.
  * Temporal folds 3-12 are the sealed confirmatory test: scoring a row there raises
    PermissionError unless unlock_test=True (--unlock-test). Dev rows are folds 0-2.
  * Prediction files are keyed on (valid, lead), never on row position. A file is
    refused when a key is not a load_stage2 row or repeats, when its rows disagree
    with its keys, or when at some lead, or in one (lead, temporal fold, valid hour)
    segment, its fields track another valid time or another lead's input
    (_check_tracking).
  * common_valid=True keeps the (station, valid) pairs scored at every lead only:
    lead 168 starts a week later, so the full tables do not share verification times.
  * Bootstrap intervals are for score differences between two forecasts, per lead:
    circular moving blocks of 5 valid days over the days present, every station of a
    drawn day kept with it, stations optionally resampled too; 95 % intervals from the
    replicates, rescaled for the block bootstrap's small-sample bias, and widened where
    the temporal folds disagree by more than 5-day blocks allow (see bootstrap).
    A lead with fewer than 4 blocks' worth of valid days gets no interval.

Prediction file (.npz; the format of scratch/preds/*.npz, harness.save_pred)
----------------------------------------------------------------------------
  rows   (n,) int          load_stage2 row indices, checked against the keys
  field  (n, 123, 127)     full 2 m temperature on the target window, degC
  valid  (n,) int64        valid time since the epoch in ns, us, ms or s, the unit read
                           from the magnitude (save_pred writes load_stage2's own unit,
                           us under pandas 3), or datetime64
  lead   (n,) int          lead, hours
  Other arrays (save_pred's config) are ignored.
"""
import argparse
import contextlib
import io
import sys
import tempfile
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm, t as student_t

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dataset import DATA_DIR, FOLD_EPOCH, load_stage2, load_stations  # noqa: E402

LEADS = (0, 24, 48, 72, 120, 168)
DEV_FOLDS = (0, 1, 2)
M_MEMBERS = 51
# the stored spread is np.std over members (ddof=0): M/(M-1) makes it the unbiased member
# variance, (M+1)/M is the spread/RMSE estimator's own factor
SPREAD_VAR_FACTOR = (M_MEMBERS / (M_MEMBERS - 1)) * ((M_MEMBERS + 1) / M_MEMBERS)
BOOT_BLOCK_DAYS = 5
BOOT_MIN_BLOCKS = 4                        # a lead needs >= 4 * block_days valid days for an interval
GROUPINGS = ("hour", "sfold", "tfold")     # valid hour, station spatial fold, temporal fold
NS_HOUR = 3_600_000_000_000
NS_DAY = 24 * NS_HOUR


# ---------------------------------------------------------------- data

def load():
    """Stage-2 rows and the scored stations' truth, aligned row by row.

    S["obs"] is (n_rows, n_stations) observed t2m, NaN where no report. S["st"] holds the
    scored stations with cy, cx (nearest CERRA cell) and iy, ix (nearest 0.25 deg cell).
    """
    d = load_stage2()
    valid = pd.DatetimeIndex(d["valid"]).as_unit("ns")
    hour = valid.hour.values.astype(int)
    assert set(np.unique(hour)) <= {0, 12}, "expected 00/12 UTC valid times only"

    st, ob = load_stations()
    st = st[st.scored].reset_index(drop=True)
    st["fold"] = st.fold.astype(int)
    tl, tn = np.radians(d["tgt_lat"]), np.radians(d["tgt_lon"])
    cy, cx, off = [], [], []
    for la, lo in zip(np.radians(st.lat.values), np.radians(st.lon.values)):
        a = np.sin((tl - la) / 2) ** 2 + np.cos(la) * np.cos(tl) * np.sin((tn - lo) / 2) ** 2
        k = np.unravel_index(a.argmin(), a.shape)
        cy.append(k[0]); cx.append(k[1]); off.append(2 * 6371.0 * np.arcsin(np.sqrt(a[k])))
    st["cy"], st["cx"] = cy, cx
    # verify_on_synop.py found these offsets in Lambert metres, an independent route
    assert np.abs(np.array(off) - st.cerra_offset_km).max() < 0.1, "nearest CERRA cells disagree"
    # the 0.25 deg grid is regular: nearest row and column separately
    st["iy"] = [int(np.abs(d["src_lat"] - v).argmin()) for v in st.lat]
    st["ix"] = [int(np.abs(d["src_lon"] - v).argmin()) for v in st.lon]
    assert (np.abs(d["src_lat"][st.iy] - st.lat) <= 0.126).all() and \
        (np.abs(d["src_lon"][st.ix] - st.lon) <= 0.126).all(), "a station lies outside the input crop"

    ob = ob[ob.sid.isin(st.sid)]
    assert not ob.duplicated(["sid", "time"]).any(), "repeated (sid, time) observations"
    piv = ob.pivot(index="time", columns="sid", values="t2m_obs")
    piv.index = pd.DatetimeIndex(piv.index).as_unit("ns")
    obs = piv.reindex(index=valid, columns=st.sid).to_numpy("float64")
    lead = d["lead"].astype(np.int64)
    key = pd.MultiIndex.from_arrays([valid.asi8, lead])
    assert key.is_unique, "load_stage2 repeats a (valid, lead) key"
    return dict(d=d, valid=valid, lead=lead, fold=d["fold"].astype(int), hour=hour,
                st=st, obs=obs, key=key)


def _at_cerra(S, field):
    """(n, 123, 127) -> (n, n_stations) at the nearest CERRA cell."""
    return np.asarray(field)[:, S["st"].cy.values, S["st"].cx.values].astype("float64")


def _at_aifs(S, channel):
    """AIFS channel (1 ens-mean, 2 spread) -> (n_rows, n_stations) at the nearest 0.25 deg cell."""
    return S["d"]["X"][:, channel, S["st"].iy.values, S["st"].ix.values].astype("float64")


def _rows_of(S, valid, lead):
    """load_stage2 row per (valid ns, lead) key; -1 where there is none."""
    return S["key"].get_indexer(pd.MultiIndex.from_arrays(
        [np.asarray(valid, np.int64), np.asarray(lead, np.int64)]))


# ---------------------------------------------------------------- forecasts

def _fc(kind, mu, sd=None, cover=None):
    return dict(kind=kind, mu=mu, sd=sd,
                cover=np.ones(len(mu), bool) if cover is None else cover)


def forecasts(S, preds=None, check_tracking=True):
    """Every scored forecast at the stations, over all load_stage2 rows.

    preds  {name: prediction file, a path or file object}; each adds a point row and a
           dressed row. Forecast = dict(kind, mu, sd, cover), mu and sd (n_rows, n_stations).
    """
    mu_a, sd_a = _at_aifs(S, 1), _at_aifs(S, 2)
    b = _at_cerra(S, S["d"]["B"])
    F = {"AIFS ENS": _fc("ensemble", mu_a, sd_a),
         "bilinear": _fc("point", b),
         "bilinear dressed": _fc("dressed", b, sd_a)}
    for name, src in (preds or {}).items():
        if name in F or name + " dressed" in F or name.startswith("CERRA"):
            raise ValueError(f"prediction name {name!r} clashes with a built-in row")
        try:
            mu, cover = load_pred(S, src, check_tracking)
        except ValueError as e:
            raise ValueError(f"prediction {name!r}: {e}") from None
        F[name] = _fc("point", mu, cover=cover)
        F[name + " dressed"] = _fc("dressed", mu, sd_a, cover)
    y = _at_cerra(S, S["d"]["Y"])
    F["CERRA (ceiling)"] = _fc("point", y)
    F["CERRA (ceiling) dressed"] = _fc("dressed", y, sd_a)
    return F


def load_pred(S, src, check_tracking=True):
    """A prediction file at the stations: (n_rows, n_stations) values, NaN on rows it lacks,
    and its row coverage. Rows are found by (valid, lead); the file's rows only confirm them."""
    z = np.load(src)
    missing = {"rows", "field", "valid", "lead"} - set(z.files)
    if missing:
        raise ValueError(f"prediction file lacks {sorted(missing)}")
    rows, field, valid, lead = (np.asarray(z[k]) for k in ("rows", "field", "valid", "lead"))
    n = len(rows)
    if n == 0:
        raise ValueError("prediction file holds no rows")
    if field.shape != (n,) + S["d"]["Y"].shape[1:] or valid.shape != (n,) or lead.shape != (n,):
        raise ValueError(f"shapes disagree: rows {rows.shape}, field {field.shape}, "
                         f"valid {valid.shape}, lead {lead.shape}")
    if not all(np.issubdtype(a.dtype, np.integer) for a in (rows, lead)):
        raise ValueError("rows and lead must be integers")
    valid = _valid_ns(S, valid)
    r = _rows_of(S, valid, lead)
    if (r < 0).any():
        raise ValueError(f"{int((r < 0).sum())} of {n} (valid, lead) keys are not load_stage2 rows")
    if len(np.unique(r)) != n:
        raise ValueError(f"{n - len(np.unique(r))} repeated (valid, lead) keys")
    if not np.array_equal(r, rows):
        raise ValueError(f"rows disagree with the (valid, lead) keys at {int((r != rows).sum())} "
                         f"of {n} entries: the file is misaligned or from another load_stage2")
    if not np.isfinite(field).all():
        raise ValueError("field has non-finite values")
    if check_tracking:
        _check_tracking(S, r, field)
    mu = np.full((len(S["lead"]), len(S["st"])), np.nan)
    mu[r] = _at_cerra(S, field)
    cover = np.zeros(len(S["lead"]), bool)
    cover[r] = True
    return mu, cover


def _valid_ns(S, valid):
    """A file's valid times as int64 ns. Integers may count ns, us, ms or s since the epoch:
    the unit is the one that puts every value within a year of the stage-2 period (the
    four differ by factors of 1000, so at most one does)."""
    if np.issubdtype(valid.dtype, np.datetime64):
        return valid.astype("datetime64[ns]").astype(np.int64)
    if not np.issubdtype(valid.dtype, np.integer):
        raise ValueError(f"valid must be datetime64 or integers since the epoch, got {valid.dtype}")
    ref = S["valid"].asi8
    lo, hi = ref.min() - 366 * NS_DAY, ref.max() + 366 * NS_DAY
    v = valid.astype("float64")
    for per in (1, 1_000, 1_000_000, 1_000_000_000):
        if ((v * per >= lo) & (v * per <= hi)).all():
            return valid.astype(np.int64) * per
    raise ValueError("valid is not a time within a year of the stage-2 period in ns, us, ms or s "
                     "since the epoch")


def _check_tracking(S, r, field, step=3, floor=0.25, max_lag_h=14 * 24, min_pairs=5):
    """Refuse a file whose fields, at a lead or in one segment of a lead, follow another
    valid time or another lead.

    Two tests on every 3rd cell, each field's domain mean removed (a bias does not count).
    A file fails if either fails anywhere.
      distance  per lead: each field against the bilinear fields of its own row and of the
                rows at the same lead 12 and 24 h either side: at least `floor` of them
                must sit nearest their own.
      tendency  per segment, a (lead, temporal fold, valid hour), the unit by which
                per-fold or per-hour predictions get stitched into one file: the change
                between consecutive fields of the segment, pattern-correlated with the
                change between the bilinear fields of the same rows. On average it must
                correlate better with its own rows' change than with that of the same
                lead shifted 12 h to 14 days either way, or of any other lead at the same
                valid times (an alternative counts where it has at least half the
                segment's pairs). A model's day-to-day change follows its input's whatever
                its bias or damping, so one misaligned segment fails however many others
                are right: a segment a day or a week off, another fold's or another lead's
                fields, shuffled fields. Pooling a lead let the aligned majority hide it.
    On the dev files (v1, the lookups, CNN v0) every lead clears the distance test at
    >= 93 % and every segment the tendency test with a mean correlation margin >= 0.07
    (>= 0.028 for bilinear + mean residual with iid N(0, 2) noise on every cell); a model
    damped to 0.1 of its anomaly, and a lead x hour climatology (no change, so the distance
    test only), clear both. In every partly misaligned copy of v2b_lookup_nohour tried (one
    fold, one fold at one lead or the 12 UTC fields 1 to 7 days off, two folds swapped, one
    fold's leads exchanged)
    each misaligned segment fails (margin <= -0.069) and each aligned one passes (>= 0.081).
    A field that knows the analysis fails the tendency test from +48 h on, its changes
    following the shortest lead's input: CERRA itself is refused, and is already the
    table's ceiling row. check_tracking=False overrides. Not caught: a misalignment inside
    a segment (a few days of a fold), or in a segment with fewer than min_pairs pairs,
    which gets the lead's distance test only. A guard against misalignment, not proof of
    alignment.
    """
    valid, lead, hour, tfold = S["valid"].asi8, S["lead"], S["hour"], S["fold"]
    Bs = S["d"]["B"][:, ::step, ::step].astype("float64")
    Bs -= Bs.mean((1, 2), keepdims=True)
    f = np.asarray(field)[:, ::step, ::step].astype("float64")
    f -= f.mean((1, 2), keepdims=True)

    def dist(i, q):
        return np.sqrt(((f[i] - Bs[q]) ** 2).mean((1, 2)))

    def corr(x, q1, q2):
        """Pattern correlation of each change x with Bs[q2] - Bs[q1]; NaN where undefined."""
        c = np.full(len(x), np.nan)
        has = (q1 >= 0) & (q2 >= 0)
        d = Bs[q2[has]] - Bs[q1[has]]
        xx = x[has]
        den = np.sqrt((xx * xx).sum((1, 2)) * (d * d).sum((1, 2)))
        with np.errstate(invalid="ignore", divide="ignore"):
            c[has] = np.where(den > 0, (xx * d).sum((1, 2)) / den, np.nan)
        return c

    bad, bad_leads = [], []
    for L in np.unique(lead[r]):
        i = np.where(lead[r] == L)[0]
        own = dist(i, r[i])
        near = np.full(len(i), np.inf)
        for h in (-24, -12, 12, 24):
            q = _rows_of(S, valid[r[i]] + h * NS_HOUR, lead[r[i]])
            has = q >= 0
            near[has] = np.minimum(near[has], dist(i[has], q[has]))
        has = np.isfinite(near)
        if has.any():
            frac = float((own[has] < near[has]).mean())
            if frac < floor:
                bad.append(f"+{L} h: {frac:.0%} of fields sit nearest their own row's bilinear "
                           "field (one row or one day off?)")
                bad_leads.append(int(L))

    segments = pd.DataFrame(dict(L=lead[r], k=tfold[r], h=hour[r])).groupby(["L", "k", "h"]).indices
    for (L, k, h), i in segments.items():
        j = i[np.argsort(valid[r[i]])]
        p1, p2 = j[:-1], j[1:]
        if len(p1) < min_pairs:
            continue
        need = max(min_pairs, -(-len(p1) // 2))
        x = f[p2] - f[p1]
        v1, v2, LL = valid[r[p1]], valid[r[p2]], lead[r[p1]]
        mine = corr(x, r[p1], r[p2])
        alts = {f"+{L2} h at the same valid times": (v1, v2, np.full(len(p1), L2))
                for L2 in np.unique(lead) if L2 != L}
        for s in range(-max_lag_h, max_lag_h + 1, 12):
            if s:
                alts[f"+{L} h, valid {s:+d} h"] = (v1 + s * NS_HOUR, v2 + s * NS_HOUR, LL)
        worst = None
        for name, (w1, w2, wl) in alts.items():
            c = corr(x, _rows_of(S, w1, wl), _rows_of(S, w2, wl))
            ok = np.isfinite(mine) & np.isfinite(c)
            if ok.sum() >= need:
                m = float((mine[ok] - c[ok]).mean())
                if worst is None or m < worst[1]:
                    worst = (name, m)
        if worst is not None and worst[1] <= 0:
            bad.append(f"+{L} h, fold {k}, {h:02d} UTC: day-to-day changes follow the bilinear "
                       f"field at {worst[0]} as well as or better than their own (mean correlation "
                       f"margin {worst[1]:+.3f})")
            bad_leads.append(int(L))
    if bad:
        shown = bad[:8] + ([f"and {len(bad) - 8} more"] if len(bad) > 8 else [])
        leads = ", ".join(f"+{L} h" for L in sorted(set(bad_leads)))
        raise ValueError(f"the file looks misaligned at {leads}: " + "; ".join(shown) + ". A field "
                         "that knows the analysis (CERRA itself) fails the same way. "
                         "check_tracking=False (--no-tracking-check) overrides")


# ---------------------------------------------------------------- scoring

def crps_gauss(y, mu, sd):
    """CRPS of N(mu, sd^2) at y, closed form (Gneiting et al. 2005); sd = 0 gives |y - mu|."""
    y, mu, sd = np.broadcast_arrays(*(np.asarray(v, "float64") for v in (y, mu, sd)))
    shape = y.shape
    y, mu, sd = y.ravel(), mu.ravel(), sd.ravel()
    if not (np.isfinite(sd).all() and (sd >= 0).all()):
        raise ValueError("spread must be finite and >= 0")
    out = np.abs(y - mu)
    p = np.where(sd > 0)[0]
    with np.errstate(over="ignore"):
        z = (y[p] - mu[p]) / sd[p]
    # a subnormal spread can overflow z; there the sd -> 0 limit |y - mu| already in out holds
    p, z = p[np.isfinite(z)], z[np.isfinite(z)]
    with np.errstate(over="ignore", under="ignore"):         # pdf(z) of a huge z is 0
        out[p] = sd[p] * (z * (2 * norm.cdf(z) - 1) + 2 * norm.pdf(z) - 1 / np.sqrt(np.pi))
    return out.reshape(shape)


def select_rows(S, folds=DEV_FOLDS, leads=LEADS, unlock_test=False):
    """load_stage2 row indices in the given temporal folds and leads."""
    sealed = sorted(set(folds) - set(DEV_FOLDS))
    if sealed and not unlock_test:
        raise PermissionError(f"folds {sealed} are the sealed confirmatory test; freeze the model, "
                              "then pass unlock_test=True (--unlock-test)")
    rows = np.where(np.isin(S["fold"], folds) & np.isin(S["lead"], leads))[0]
    return _check_sealed(S, rows, unlock_test)


def _check_sealed(S, rows, unlock_test=False):
    rows = np.asarray(rows)
    if rows.dtype == bool:
        assert len(rows) == len(S["lead"]), "a boolean rows mask must cover all load_stage2 rows"
        rows = np.where(rows)[0]
    assert np.issubdtype(rows.dtype, np.integer), f"rows must be indices, got {rows.dtype}"
    assert len(np.unique(rows)) == len(rows), "rows repeat"
    folds = np.unique(S["fold"][rows])
    sealed = sorted(set(folds.tolist()) - set(DEV_FOLDS))
    if sealed and not unlock_test:
        raise PermissionError(f"rows in folds {sealed}: folds 3-12 are the sealed confirmatory "
                              "test; freeze the model, then pass unlock_test=True (--unlock-test)")
    return rows


def _station_times(S, F, rows, unlock_test=False, intersect=False, common_valid=False):
    """The scored station-times, one per (row, station) with an observation and every forecast.

    Returns T (keys per station-time) and E {name: err, crps, var}, all aligned.
    """
    rows = _check_sealed(S, rows, unlock_test)
    cover = np.ones(len(rows), bool)
    for name, f in F.items():
        c = f["cover"][rows]
        if not c.all() and not intersect:
            raise ValueError(f"{name}: no forecast for {int((~c).sum())} of {len(rows)} rows; "
                             "intersect=True (--intersect) scores every forecast on the rows all cover")
        cover &= c
    rows = rows[cover]
    ok = np.isfinite(S["obs"][rows])
    for name, f in F.items():
        if not np.isfinite(f["mu"][rows][ok]).all():
            raise ValueError(f"{name}: non-finite forecast at a scored station-time")
        if f["sd"] is not None:
            sd = f["sd"][rows][ok]
            if not (np.isfinite(sd).all() and (sd >= 0).all()):
                raise ValueError(f"{name}: spread must be finite and >= 0 at every scored station-time")
    if common_valid:
        # keep a (valid, station) pair only where it is scored at every lead present
        uv, vi = np.unique(S["valid"].asi8[rows], return_inverse=True)
        n_lead = len(np.unique(S["lead"][rows]))
        count = np.zeros((len(uv), ok.shape[1]), int)
        np.add.at(count, vi, ok)
        ok &= count[vi] == n_lead
    ri, si = np.nonzero(ok)
    r = rows[ri]
    obs = S["obs"][r, si]
    T = dict(row=r, station=si, lead=S["lead"][r], hour=S["hour"][r], tfold=S["fold"][r],
             sfold=S["st"].fold.values[si], day=S["valid"].asi8[r] // NS_DAY, obs=obs)
    E = {}
    for name, f in F.items():
        mu = f["mu"][r, si]
        err = mu - obs
        if f["sd"] is None:
            E[name] = dict(err=err, crps=np.abs(err), var=None)
        else:
            sd = f["sd"][r, si]
            E[name] = dict(err=err, crps=crps_gauss(obs, mu, sd), var=sd ** 2)
    return T, E


def score(S, F, rows, by=(), **kw):
    """Long table: one row per (lead, *by, forecast) with n, me, rmse, crps, spread_rmse.

    by  any of GROUPINGS: 'hour' (valid 00/12 UTC), 'sfold' (station spatial fold),
        'tfold' (temporal fold). kw: unlock_test, intersect, common_valid.
    """
    by = [by] if isinstance(by, str) else list(by)
    assert set(by) <= set(GROUPINGS), f"by must be drawn from {GROUPINGS}"
    T, E = _station_times(S, F, rows, **kw)
    keys = ["lead"] + by
    g = pd.DataFrame({k: T[k] for k in keys})
    out = []
    for name, f in F.items():
        e = E[name]
        a = g.assign(n=1, me=e["err"], se=e["err"] ** 2, crps=e["crps"],
                     var=np.nan if e["var"] is None else e["var"]).groupby(keys).agg(
            n=("n", "sum"), me=("me", "mean"), se=("se", "mean"), crps=("crps", "mean"),
            var=("var", "mean"))
        a["rmse"] = np.sqrt(a.se)
        a["spread_rmse"] = np.sqrt(a["var"] * SPREAD_VAR_FACTOR) / a.rmse
        out.append(a.reset_index().assign(forecast=name, kind=f["kind"]))
    t = pd.concat(out, ignore_index=True).sort_values(keys, kind="stable", ignore_index=True)
    assert (t.groupby(keys).n.nunique() == 1).all(), "forecasts scored on different station-times"
    return t[keys + ["forecast", "kind", "n", "me", "rmse", "crps", "spread_rmse"]]


# ---------------------------------------------------------------- bootstrap

def _block_days(rng, K, block, n_boot):
    """(n_boot, K) day indices: circular moving-block resamples (Politis & Romano 1992),
    ceil(K/block) runs of `block` consecutive days that wrap from the last day to the
    first, cut to K days. Every day has the same expected count, 1."""
    L = min(block, K)
    starts = rng.integers(0, K, size=(n_boot, -(-K // L)))
    return ((starts[:, :, None] + np.arange(L)) % K).reshape(n_boot, -1)[:, :K]


def bootstrap(S, F, rows, a, b, n_boot=2000, block_days=BOOT_BLOCK_DAYS,
              resample_stations=False, seed=0, level=0.95, **kw):
    """Score differences a - b per lead, with block-bootstrap intervals.

    The station-times are those score() uses for the same F and kw, so the estimate is
    the difference of two table rows. Valid days (UTC dates) are drawn in circular moving
    blocks of block_days consecutive days over the days present, in order (a block may
    straddle a fold gap, or wrap from the last day to the first); every station of a
    drawn day comes with it.

    The interval is estimate + c * (replicate quantiles - estimate). Days only:
    c = sqrt(K/(K-L)) * t_nu/z, nu = 1.5 K/L, for K days and blocks of L. The circular
    block's replicate variance is (1 - L/K) times the sampling variance on serially
    uncorrelated days, and the block variance estimate has about 1.5 K/L degrees of
    freedom (Kuensch 1989), so a z-width interval from ~12 blocks undercovers. On iid
    synthetic data this covers 94-96 % at 20-62 days, where the plain moving block
    covered 82-92 %. Serial correlation in the day effects lowers coverage (93 % at
    AR(1) 0.5).

    resample_stations also redraws the C stations with replacement, crossed with the
    days. That pigeonhole resample counts the station-time noise three times (Owen
    2007), so c also rescales the replicates' linearised variance VD + VS + VI (day,
    station and interaction parts, read off the same replicates) to the crossed
    sampling variance VD/(1-L/K) + max(VS/(1-1/C) - VI/((1-L/K)(1-1/C)), 0), never
    narrower than days only; nu then combines the two parts (Satterthwaite). On
    synthetic day + station + noise data at the dev size this covers 94-95 % from noise
    only to station-dominated, where the uncorrected crossed resample covered 95-99.7 %.

    Temporal folds. 5-day blocks carry dependence up to about 5 days. A difference that
    drifts over weeks (an ME difference that moves with the season, a model refitted per
    fold) makes the folds disagree by more than the blocks allow, and the block interval
    is then too narrow: on the dev rows the per-fold ME intervals of a lookup model
    against bilinear were mutually disjoint. So with G >= 3 temporal folds at a lead, the
    between-fold variance VF = G/(G-1) sum_g U_g^2 (U_g the fold totals of the linearised
    difference; G-1 degrees of freedom) is set against the block variance VB; its excess
    tau = max(VF - VB, 0) is added as a between-fold component (DerSimonian & Laird 1986),
    and the interval widened to cover estimate +- t_nu sqrt(VB + tau [+ station part]), nu
    by Satterthwaite. tau = 0 leaves the block interval as it is. On synthetic data on the
    real +24 h and +168 h layouts (3 folds, 600-1000 data sets per case) this covers
    95-96 % with short memory (mean width 1.2 x the true 95 % width), 93.5-94.5 % for the
    day structure of the real CRPS differences, 88 % with a fold-level step (sd 0.08)
    where blocks alone covered 57-60 %, and 83-85 % with AR(1) day effects at lag-1
    0.88-0.91 (the real ME differences) where blocks alone covered 62-70 %; crossed with
    stations 89 % there (82 % before). Three folds cannot do better: VF has 2 degrees of
    freedom. With fewer than 3 folds (one or two scored) there is no check.

    A lead with fewer than BOOT_MIN_BLOCKS * block_days valid days gets lo = hi = NaN and
    a warning: too few distinct replicates for an interval.
    Returns lead, a, b, metric (me, rmse, crps), estimate, lo, hi, n, days, folds (G) and
    fold_share = tau / (VB + tau), the between-fold part of the day variance (NaN without
    the check).
    """
    if int(block_days) != block_days or block_days < 1:
        raise ValueError(f"block_days must be a positive integer, got {block_days}")
    T, E = _station_times(S, F, rows, **kw)
    rng = np.random.default_rng(seed)
    q = np.array([(1 - level) / 2, (1 + level) / 2])
    zq = norm.ppf((1 + level) / 2)
    n_st = len(S["st"])
    out = []
    for L in np.unique(T["lead"]):
        m = T["lead"] == L
        days, di = np.unique(T["day"][m], return_inverse=True)
        K = len(days)
        day_fold = np.zeros(K, int)
        day_fold[di] = T["tfold"][m]
        gi = np.unique(day_fold, return_inverse=True)[1]
        G = int(gi.max()) + 1
        cell = di * n_st + T["station"][m]

        def tot(x):
            return np.bincount(cell, x, K * n_st).reshape(K, n_st)

        ea, eb = E[a]["err"][m], E[b]["err"][m]
        sums = dict(n=tot(np.ones(m.sum())), ea=tot(ea), eb=tot(eb), sa=tot(ea ** 2),
                    sb=tot(eb ** 2), ca=tot(E[a]["crps"][m]), cb=tot(E[b]["crps"][m]))
        W = np.ones((n_boot + 1, K))                    # day weights: counts in each resample
        W[1:] = 0
        np.add.at(W[1:], (np.arange(n_boot)[:, None], _block_days(rng, K, block_days, n_boot)), 1)
        V = np.ones((n_boot + 1, n_st))
        if resample_stations:
            V[1:] = [np.bincount(rng.integers(0, n_st, n_st), minlength=n_st) for _ in range(n_boot)]
        # row 0 is the full sample, rows 1.. the replicates
        A = {k: np.einsum("bk,km,bm->b", W, s, V) for k, s in sums.items()}
        n = A["n"]
        assert (n > 0).all(), "a bootstrap replicate drew no station-times"
        ra, rb = np.sqrt(A["sa"] / n), np.sqrt(A["sb"] / n)
        diff = dict(me=(A["ea"] - A["eb"]) / n, rmse=ra - rb, crps=(A["ca"] - A["cb"]) / n)
        enough = K >= BOOT_MIN_BLOCKS * block_days
        if not enough:
            warnings.warn(f"lead +{L} h, {a} - {b}: {K} valid days, fewer than {BOOT_MIN_BLOCKS} "
                          f"blocks of {block_days}: no interval", stacklevel=2)
        Lb = min(block_days, K)
        alpha, nu_d = 1 - Lb / K, 1.5 * K / Lb
        N = n[0]
        # each difference's gradient in the sums at the full sample: its linearisation
        grad = dict(me=dict(ea=1 / N, eb=-1 / N, n=-diff["me"][0] / N),
                    rmse=dict(sa=1 / (2 * N * ra[0]) if ra[0] > 0 else 0.0,
                              sb=-1 / (2 * N * rb[0]) if rb[0] > 0 else 0.0,
                              n=-(ra[0] - rb[0]) / (2 * N)),
                    crps=dict(ca=1 / N, cb=-1 / N, n=-diff["crps"][0] / N))
        for k, v in diff.items():
            lo = hi = share = np.nan
            if enough:
                c, nu = 1 / np.sqrt(alpha), nu_d
                u = sum(g * sums[s] for s, g in grad[k].items())     # (K, n_st), sums to 0
                Wd = W[1:] - 1
                VD = np.var(Wd @ u.sum(1))
                d_part, s_part = VD / alpha, 0.0
                if resample_stations:
                    Vd = V[1:] - 1
                    VS = np.var(Vd @ u.sum(0))
                    VI = np.var(np.einsum("bk,km,bm->b", Wd, u, Vd))
                    beta = 1 - 1 / n_st
                    s_part = max(VS / beta - VI / (alpha * beta), 0.0)
                    have, want = VD + VS + VI, d_part + s_part
                    if have > 0:
                        c = np.sqrt(want / have)
                    if want > 0:
                        nu = want ** 2 / (d_part ** 2 / nu_d + s_part ** 2 / max(n_st - 1, 1))
                c *= student_t.ppf((1 + level) / 2, nu) / zq
                lo, hi = v[0] + c * (np.quantile(v[1:], q) - v[0])
                if G >= 3:
                    U = np.bincount(gi, u.sum(1), G)                     # fold totals
                    tau = max(G / (G - 1) * (U ** 2).sum() - d_part, 0.0)
                    share = tau / (d_part + tau) if d_part + tau > 0 else 0.0
                    if tau > 0:
                        var = d_part + tau + s_part
                        nu_t = var ** 2 / (d_part ** 2 / nu_d + tau ** 2 / (G - 1)
                                           + s_part ** 2 / max(n_st - 1, 1))
                        hw = student_t.ppf((1 + level) / 2, nu_t) * np.sqrt(var)
                        lo, hi = min(lo, v[0] - hw), max(hi, v[0] + hw)
            out.append(dict(lead=int(L), a=a, b=b, metric=k, estimate=v[0], lo=lo, hi=hi,
                            n=int(n[0]), days=K, folds=G, fold_share=share))
    return pd.DataFrame(out)


# ---------------------------------------------------------------- output

def _fmt(v, col):
    if pd.isna(v):
        return ""
    if col in ("n", "days", "lead", "hour", "sfold", "tfold", "folds"):
        return str(int(v))
    return f"{v:.3f}" if isinstance(v, (float, np.floating)) else str(v)


def _md_table(df, cols, heads):
    lines = ["| " + " | ".join(heads) + " |",
             "|" + "|".join("---:" if c not in ("forecast", "kind", "a", "b", "metric") else "---"
                            for c in cols) + "|"]
    lines += ["| " + " | ".join(_fmt(r[c], c) for c in cols) + " |" for _, r in df.iterrows()]
    return lines


def tables_md(t, title, note):
    """One markdown table per lead from a score() table."""
    by = [c for c in GROUPINGS if c in t.columns]
    cols = by + ["forecast", "kind", "n", "me", "rmse", "crps", "spread_rmse"]
    heads = by + ["forecast", "kind", "n", "ME", "RMSE", "CRPS", "spread/RMSE"]
    lines = [f"# {title}", "", note, ""]
    for L, g in t.groupby("lead", sort=True):
        lines += [f"## Lead +{L} h", ""] + _md_table(g, cols, heads) + [""]
    return "\n".join(lines)


def bootstrap_md(bs, title, note):
    cols = ["a", "b", "metric", "estimate", "lo", "hi", "n", "days", "folds", "fold_share"]
    heads = ["A", "B", "metric", "A - B", "2.5 %", "97.5 %", "n", "days", "folds", "fold share"]
    lines = [f"# {title}", "", note, ""]
    for L, g in bs.groupby("lead", sort=True):
        lines += [f"## Lead +{L} h", ""] + _md_table(g, cols, heads) + [""]
    return "\n".join(lines)


# categorical slots in fixed order (dataviz reference palette, light surface)
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]


def plot_crps(t, diff, path, subtitle=""):
    """CRPS by lead (left) and its difference from AIFS ENS with 95 % intervals (right).

    t     score() table; its ensemble and dressed rows are drawn, dressed CERRA in grey
    diff  bootstrap() rows of crps differences against AIFS ENS
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ink, ink2, grid, surface, ref = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb", "#8f8e88"
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11, 4.8), dpi=150, facecolor=surface)
    names = [n for n in dict.fromkeys(t.forecast)
             if t.kind[t.forecast == n].iloc[0] != "point" and not n.startswith("CERRA")]
    color = {n: SERIES[i % len(SERIES)] for i, n in enumerate(names)}
    style = dict(lw=2, marker="o", ms=7, mec=surface, mew=2, solid_capstyle="round", zorder=3)
    for n in names:
        g = t[t.forecast == n].sort_values("lead")
        ax.plot(g.lead, g.crps, color=color[n], label=n, **style)
    g = t[t.forecast == "CERRA (ceiling) dressed"].sort_values("lead")
    if len(g):
        ax.plot(g.lead, g.crps, color=ref, lw=2, label="CERRA (ceiling) dressed", zorder=2)
    bx.axhline(0, color=ref, lw=1.5, zorder=2)
    others = [n for n in names if n in set(diff.a)]
    for i, n in enumerate(others):
        g = diff[(diff.a == n) & (diff.metric == "crps")].sort_values("lead")
        x = g.lead + 3.0 * (i - (len(others) - 1) / 2)          # dodge, in hours
        bx.errorbar(x, g.estimate, yerr=[g.estimate - g.lo, g.hi - g.estimate], color=color[n],
                    ecolor=color[n], elinewidth=1.5, capsize=0, **style)
    ax.set_ylabel("CRPS (°C)", color=ink2)
    bx.set_ylabel("CRPS minus AIFS ENS (°C); below 0 is better", color=ink2)
    for a in (ax, bx):
        a.set_facecolor(surface)
        a.set_xticks(LEADS)
        a.set_xlabel("lead (h)", color=ink2)
        a.grid(axis="y", color=grid, lw=1)
        for s in ("top", "right", "left"):
            a.spines[s].set_visible(False)
        a.spines["bottom"].set_color(grid)
        a.tick_params(colors=ink2, length=0)
    ax.legend(frameon=False, fontsize=8, loc="upper left", labelcolor=ink)
    fig.suptitle("CRPS by lead at the scored SYNOP stations", x=0.01, y=0.98, ha="left",
                 color=ink, fontsize=12)
    fig.text(0.01, 0.94, subtitle, color=ink2, fontsize=8, ha="left", va="top", linespacing=1.5)
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    fig.savefig(path, facecolor=surface)
    plt.close(fig)


# ---------------------------------------------------------------- self-check

# dev folds 0-2, all valid times, per lead: from scratch/harness.py, which agreed with two
# earlier independent scripts
EXPECTED_RMSE = {"bilinear": [1.718, 1.610, 1.719, 1.876, 2.268, 2.833],
                 "AIFS ENS": [1.755, 1.655, 1.760, 1.912, 2.291, 2.846],
                 "CERRA (ceiling)": [1.233, 1.233, 1.233, 1.239, 1.250, 1.262]}
EXPECTED_CRPS = {"AIFS ENS": [1.086, 0.921, 0.976, 1.064, 1.280, 1.596]}
EXPECTED_N = [8501, 8336, 8170, 8004, 7672, 7341]


def _npz(**arrays):
    buf = io.BytesIO()
    np.savez(buf, **arrays)
    buf.seek(0)
    return buf


def _pred_file(S, rows, field, keys_from=None):
    k = rows if keys_from is None else keys_from
    return _npz(rows=rows, field=np.asarray(field, "float32"),
                valid=S["valid"].asi8[k], lead=S["lead"][k])


def _synthetic(obs, lead=0, fold=None):
    """A stand-in for load() over synthetic station-times: one row per 12 h, one lead.
    fold (per row, non-decreasing) labels temporal folds, 5 days apart as the real ones."""
    n, k = obs.shape
    fold = np.zeros(n, int) if fold is None else np.asarray(fold, int)
    v = pd.DatetimeIndex(FOLD_EPOCH + pd.to_timedelta(np.arange(n) * 12 + fold * 120, "h")).as_unit("ns")
    return dict(valid=v, lead=np.full(n, lead, np.int64), fold=fold, hour=v.hour.values,
                st=pd.DataFrame({"fold": np.zeros(k, int)}), obs=obs)


def _refused(call, exc, match=""):
    try:
        call()
    except exc as e:
        assert match in str(e), f"refused for the wrong reason: {e}"
        return True
    raise AssertionError(f"not refused: expected {exc.__name__} {match!r}")


def self_check(S=None):
    """Plain asserts; returns the names of the checks that passed."""
    from scipy.integrate import quad
    S = load() if S is None else S
    done = []

    # CRPS known answers
    assert abs(crps_gauss(0.0, 0.0, 1.0) - (np.sqrt(2) - 1) / np.sqrt(np.pi)) < 1e-12
    assert crps_gauss(1.3, 0.2, 0.0) == abs(1.3 - 0.2)
    assert abs(crps_gauss(1.3, 0.2, 1e-9) - 1.1) < 1e-8
    y, mu, sd = -0.4, 0.7, 1.9
    integral = (quad(lambda x: norm.cdf(x, mu, sd) ** 2, -np.inf, y)[0]
                + quad(lambda x: norm.sf(x, mu, sd) ** 2, y, np.inf)[0])
    assert abs(crps_gauss(y, mu, sd) - integral) < 1e-7
    _refused(lambda: crps_gauss(0.0, 0.0, -1.0), ValueError, "spread")
    # a subnormal spread overflows z = (y - mu)/sd: the limit |y - mu| must stand, not inf
    tiny = crps_gauss(np.ones(5), 0.0, [1e-300, 1e-308, 5e-309, 1e-310, 5e-324])
    assert np.isfinite(tiny).all() and np.allclose(tiny, 1.0, rtol=0, atol=1e-12), tiny
    # synthetic stations: truth drawn from the forecast itself
    rng = np.random.default_rng(7)
    n, k = 2000, 100
    mu, sd, z = rng.normal(size=(n, k)), rng.uniform(0.5, 2.0, (n, k)), rng.standard_normal((n, k))
    syn = _synthetic(mu + sd * z)
    ts = score(syn, {"g": _fc("ensemble", mu, sd)}, np.arange(n))
    assert abs(ts.crps[0] / (sd.mean() / np.sqrt(np.pi)) - 1) < 0.005    # E CRPS = sd / sqrt(pi)
    # a reliable 51-member ensemble, its spread stored as aifs.npz stores it: np.std, ddof=0
    sigma = rng.uniform(0.5, 2.0, (n, k))
    members = mu[..., None] + sigma[..., None] * rng.standard_normal((n, k, M_MEMBERS))
    syn = _synthetic(mu + sigma * rng.standard_normal((n, k)))
    ts = score(syn, {"g": _fc("ensemble", members.mean(-1), members.std(-1))}, np.arange(n))
    assert abs(ts.spread_rmse[0] - 1) < 0.005, ts.spread_rmse[0]     # ddof ignored: 0.990
    del members
    done.append("crps and spread/RMSE known answers (subnormal spread; ddof=0 spread of a "
                "reliable 51-member ensemble gives 1)")

    # the reference numbers
    dev = select_rows(S)
    F = forecasts(S)
    t = score(S, F, dev)
    piv = {c: t.pivot(index="forecast", columns="lead", values=c) for c in ("rmse", "crps", "n")}
    for name, want in EXPECTED_RMSE.items():
        got = piv["rmse"].loc[name, list(LEADS)].values
        assert np.allclose(got, want, atol=6e-4), f"{name} RMSE {got.round(4)} != {want}"
    for name, want in EXPECTED_CRPS.items():
        got = piv["crps"].loc[name, list(LEADS)].values
        assert np.allclose(got, want, atol=6e-4), f"{name} CRPS {got.round(4)} != {want}"
    assert (piv["n"][list(LEADS)].values == EXPECTED_N).all(), piv["n"]
    assert np.allclose(piv["rmse"].loc["bilinear dressed"], piv["rmse"].loc["bilinear"], rtol=0, atol=0)
    done.append("reference RMSE, CRPS and n")
    assert (t.groupby("lead").n.nunique() == 1).all() and set(t.lead) == set(LEADS)
    done.append("identical n across forecasts per lead")

    # extraction agrees with verify_on_synop.py's independent four-way table
    T, E = _station_times(S, F, dev)
    a = pd.DataFrame({"sid": S["st"].sid.values[T["station"]], "lead_h": T["lead"],
                      "time": S["valid"][T["row"]].as_unit("ns"), "obs": T["obs"],
                      "mu": T["obs"] + E["AIFS ENS"]["err"], "sd": np.sqrt(E["AIFS ENS"]["var"]),
                      "bil": T["obs"] + E["bilinear dressed"]["err"],
                      "crps_bd": E["bilinear dressed"]["crps"]})
    fw = pd.read_parquet(DATA_DIR / "synop_fourway.parquet")
    fw["time"] = pd.DatetimeIndex(fw.time).as_unit("ns")
    m = a.merge(fw, on=["sid", "time", "lead_h"])
    assert len(m) > 40000, len(m)
    assert np.abs(m.mu - m.t2m_aifs).max() < 1e-4 and np.abs(m.sd - m.aifs_sd).max() < 1e-4
    assert np.abs(m.obs - m.t2m_obs).max() < 1e-9
    # a dressed row carries the spread of its own station-time
    want = crps_gauss(m.t2m_obs, m.bil, m.aifs_sd)
    assert np.abs(m.crps_bd - want).max() < 1e-4, "dressing uses the wrong spread"
    done.append(f"extraction matches synop_fourway ({len(m)} station-times)")

    # a zero-correction model is bilinear, exactly
    B = S["d"]["B"]
    F0 = forecasts(S, {"b+0": _pred_file(S, dev, B[dev] + 0.0 * S["d"]["R"][dev])})
    t0 = score(S, F0, dev).set_index(["lead", "forecast"])
    for x, ref in (("b+0", "bilinear"), ("b+0 dressed", "bilinear dressed")):
        u, v = t0.xs(x, level="forecast"), t0.xs(ref, level="forecast")
        cols = ["n", "me", "rmse", "crps", "spread_rmse"]
        assert u[cols].equals(v[cols]), f"{x} differs from {ref}"
    done.append("zero-correction model equals bilinear exactly")

    # key alignment
    perm = np.random.default_rng(1).permutation(len(dev))
    mu_plain, _ = load_pred(S, _pred_file(S, dev, B[dev]))
    mu_shuf, _ = load_pred(S, _pred_file(S, dev[perm], B[dev][perm]))
    assert np.array_equal(mu_plain, mu_shuf, equal_nan=True), "a shuffled file was not realigned"
    sub = dev[dev + 1 < len(S["lead"])]
    _refused(lambda: load_pred(S, _pred_file(S, sub + 1, B[sub], keys_from=sub)), ValueError, "rows disagree")
    _refused(lambda: load_pred(S, _pred_file(S, sub, B[sub], keys_from=sub + 1)), ValueError, "rows disagree")
    _refused(lambda: load_pred(S, _pred_file(S, dev[1:], B[dev[:-1]])), ValueError, "misaligned")
    day_before = _rows_of(S, S["valid"].asi8[dev] - NS_DAY, S["lead"][dev])
    h = day_before >= 0
    _refused(lambda: load_pred(S, _pred_file(S, dev[h], B[day_before[h]])), ValueError, "misaligned")
    late = _npz(rows=dev, field=B[dev], valid=S["valid"].asi8[dev] + NS_HOUR, lead=S["lead"][dev])
    _refused(lambda: load_pred(S, late), ValueError, "not load_stage2 rows")
    rep = np.r_[dev, dev[:1]]
    _refused(lambda: load_pred(S, _pred_file(S, rep, B[rep])), ValueError, "repeated")
    done.append("key alignment: shuffled realigned, off-by-one rows/keys/fields refused")

    # valid units: harness.save_pred writes load_stage2's own unit (us under pandas 3) and a
    # config array; any of ns/us/ms/s or datetime64 loads to the same rows
    native = np.asarray(S["d"]["valid"].values)
    harness = _npz(rows=dev, field=np.asarray(B[dev], "float32"), lead=S["d"]["lead"][dev],
                   valid=native[dev].astype("int64"), config=np.array(repr({"seed": 0})))
    assert np.array_equal(load_pred(S, harness)[0], mu_plain, equal_nan=True), "save_pred file"
    for unit in ("s", "ms", "us", "ns"):
        vu = S["valid"][dev].values.astype(f"datetime64[{unit}]")
        for vv in (vu.astype("int64"), vu):
            f = _npz(rows=dev, field=B[dev], valid=vv, lead=S["lead"][dev])
            assert np.array_equal(load_pred(S, f)[0], mu_plain, equal_nan=True), f"valid in {unit}"
    odd = _npz(rows=dev, field=B[dev], valid=S["valid"].asi8[dev] // 7, lead=S["lead"][dev])
    _refused(lambda: load_pred(S, odd), ValueError, "within a year")
    done.append("valid in ns/us/ms/s or datetime64 and harness.save_pred's format load alike")

    # tracking: a model (bilinear + mean residual) with fields moved in time or lead
    M0 = B[dev] + S["d"]["R"][dev].mean(0)
    ld, fo, ho = S["lead"][dev], S["fold"][dev], S["hour"][dev]

    def moved(*moves):
        """M0 with fields moved: each (sel, hours, from_lead) gives the dev rows in sel the
        field of valid - hours at lead from_lead (None: their own). Rows whose source is not
        a dev row are dropped."""
        src = dev.copy()
        for sel, hours, from_lead in moves:
            src[sel] = _rows_of(S, S["valid"].asi8[dev[sel]] - hours * NS_HOUR,
                                ld[sel] if from_lead is None else np.full(sel.sum(), from_lead))
        j = np.searchsorted(dev, src).clip(0, len(dev) - 1)
        ok = dev[j] == src                                # the source is a dev row
        return _pred_file(S, dev[ok], M0[j[ok]])
    every = np.ones(len(dev), bool)
    for f, where in ((moved((ld == 168, 24, None)), "+168 h"),     # one lead a day late
                     (moved((ld == 168, 0, 0)), "+168 h"),         # +168 h keys hold +0 h fields
                     (moved((ld == 24, 0, 48)), "+24 h"),          # neighbouring leads swapped
                     (moved((every, 168, None)), "+0 h"),          # every lead a week late
                     (moved((every, -96, None)), "+0 h")):         # every lead 4 days early
        _refused(lambda: load_pred(S, f), ValueError, where)

    # one segment misaligned, the rest right (per-fold or per-hour predictions stitched with
    # one part off): refused, naming the bad segments and none of the aligned ones
    def why(f):
        try:
            load_pred(S, f)
        except ValueError as e:
            return str(e)
        raise AssertionError("a partly misaligned file was accepted")
    day, gap = 24, 26 * 24                                # folds start 26 days apart
    for f, where, clean in (
            (moved((fo == 2, day, None)), "fold 2", ("fold 0", "fold 1")),
            (moved(((fo == 2) & (ld == 24), day, None)), "misaligned at +24 h:", ("fold 0", "fold 1")),
            (moved((fo == 1, 2 * day, None)), "fold 1", ("fold 0", "fold 2")),
            (moved((fo == 1, -gap, None), (fo == 2, gap, None)), "fold 1", ("fold 0",)),   # swapped
            (moved((ho == 12, day, None)), "12 UTC", ("00 UTC",)),
            (moved(((fo == 2) & (ld == 0), 0, 168), ((fo == 2) & (ld == 168), 0, 0)),
             "misaligned at +0 h, +168 h:", ("fold 0", "fold 1")),
            (moved(((fo == 2) & (ld == 24), 0, 48), ((fo == 2) & (ld == 48), 0, 24)),
             "misaligned at +24 h, +48 h:", ("fold 0", "fold 1"))):
        msg = why(f)
        assert where in msg and not any(c in msg for c in clean), msg
    perm = np.arange(len(dev))
    for L in LEADS:
        i = np.where(S["lead"][dev] == L)[0]
        perm[i] = np.random.default_rng(L).permutation(i)
    _refused(lambda: load_pred(S, _pred_file(S, dev, M0[perm])), ValueError, "misaligned")
    clim = np.zeros_like(M0)
    for L in LEADS:
        for h in (0, 12):
            i = (S["lead"][dev] == L) & (S["hour"][dev] == h)
            clim[i] = M0[i].mean(0)
    noise = np.random.default_rng(2).normal(0, 1, M0.shape).astype("float32")
    for ok_model in (M0, M0 + noise, clim + 0.1 * (M0 - clim), clim):    # noisy, damped, constant
        load_pred(S, _pred_file(S, dev, ok_model))
    Y = S["d"]["Y"]
    _refused(lambda: load_pred(S, _pred_file(S, dev, Y[dev])), ValueError, "+48 h")   # knows the analysis
    load_pred(S, _pred_file(S, dev, Y[dev]), check_tracking=False)
    done.append("tracking: one lead a day late, a wrong lead, every lead a week late or 4 days "
                "early, shuffled, CERRA refused; one fold a day or two late (at every lead or one), "
                "two folds swapped, the 12 UTC fields a day late, one fold's leads exchanged refused "
                "by segment; noisy, damped, constant models accepted")

    # partial coverage: refused, or every forecast shrinks to the shared rows
    l24 = dev[S["lead"][dev] == 24]
    Fp = forecasts(S, {"b24": _pred_file(S, l24, B[l24])})
    _refused(lambda: score(S, Fp, dev), ValueError, "intersect")
    tp = score(S, Fp, dev, intersect=True)
    assert set(tp.lead) == {24} and (tp.n == EXPECTED_N[1]).all()
    done.append("partial files refused or intersected")

    # sealed folds: library and CLI
    test = np.where(~np.isin(S["fold"], DEV_FOLDS))[0]
    _refused(lambda: select_rows(S, folds=(3,)), PermissionError)
    _refused(lambda: select_rows(S, folds=(0, 1, 2, 12)), PermissionError)
    _refused(lambda: score(S, F, test[:5]), PermissionError)
    _refused(lambda: score(S, F, np.r_[dev[:5], test[:1]]), PermissionError)
    _refused(lambda: bootstrap(S, F, test[:50], "bilinear", "AIFS ENS", n_boot=10), PermissionError)
    mask = np.zeros(len(S["lead"]), bool); mask[test[0]] = True
    _refused(lambda: score(S, F, mask), PermissionError)
    g = globals()
    real_load = g["load"]

    class Loaded(Exception):
        pass

    def tripwire():
        raise Loaded("the CLI got past its argument checks")
    g["load"] = tripwire                     # a broken guard trips here, before any scoring
    try:
        for argv in (["--folds", "3"], ["--folds", "0", "1", "2", "5"]):
            with contextlib.redirect_stderr(io.StringIO()):
                _refused(lambda: main(argv), SystemExit)
        done.append("sealed folds 3-12 refused (library and CLI)")

        # --pred: names unique, paths may hold '='
        assert _parse_pred("cnn=a.npz") == ("cnn", "a.npz")
        assert _parse_pred("runs/a.npz") == ("a", "runs/a.npz")
        assert _parse_pred("lookup=runC/lr=0.002/model.npz") == ("lookup", "runC/lr=0.002/model.npz")
        assert _parse_pred("runC/lr=0.002/model.npz") == ("model", "runC/lr=0.002/model.npz")
        assert _parse_pred("./lr=0.002/model.npz") == ("model", "./lr=0.002/model.npz")
        with tempfile.TemporaryDirectory() as tmp:
            for d in ("runA", "runB", "runC/lr=0.002"):
                (Path(tmp) / d).mkdir(parents=True)
                (Path(tmp) / d / "model.npz").write_bytes(b"")
            for argv in (["--pred", f"{tmp}/runA/model.npz", "--pred", f"{tmp}/runB/model.npz"],
                         ["--pred", f"x={tmp}/runA/model.npz", "--pred", f"x={tmp}/runB/model.npz"]):
                err = io.StringIO()
                with contextlib.redirect_stderr(err):
                    _refused(lambda: main(argv), SystemExit)
                assert "repeats" in err.getvalue(), err.getvalue()
            for argv in (["--pred", f"lookup={tmp}/runC/lr=0.002/model.npz"],
                         ["--pred", f"{tmp}/runC/lr=0.002/model.npz", "--pred", f"a={tmp}/runA/model.npz"]):
                with contextlib.redirect_stderr(io.StringIO()):
                    _refused(lambda: main(argv), Loaded)
            # a partly misaligned file: the CLI stops before scoring and names it
            (Path(tmp) / "late.npz").write_bytes(moved(((fo == 2) & (ld == 168), day, None)).getvalue())
            g["load"] = lambda: S
            err = io.StringIO()
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()) as out:
                _refused(lambda: main(["--pred", f"late={tmp}/late.npz"]), SystemExit)
            assert "prediction 'late'" in err.getvalue() and "+168 h, fold 2" in err.getvalue(), err.getvalue()
            assert out.getvalue() == "", "the CLI printed a table for a misaligned file"
    finally:
        g["load"] = real_load
    done.append("--pred: repeated names refused, paths with '=' parsed, a partly misaligned file "
                "stops the CLI")

    # shared valid times and groupings
    tc = score(S, F, dev, common_valid=True)
    assert tc.n.nunique() == 1, "common_valid left different station-times per lead"
    Tc, _ = _station_times(S, F, dev, common_valid=True)
    pairs = {L: set(zip(Tc["day"][Tc["lead"] == L] * 24 + Tc["hour"][Tc["lead"] == L],
                        Tc["station"][Tc["lead"] == L])) for L in LEADS}
    assert all(pairs[L] == pairs[0] for L in LEADS)
    ce = tc[tc.forecast == "CERRA (ceiling)"]
    assert np.ptp(ce.rmse) < 1e-12 and np.ptp(ce.crps) < 1e-12, "CERRA varies with lead on shared times"
    for by in ("hour", "sfold", "tfold", ["hour", "sfold"]):
        tg = score(S, F, dev, by=by)
        assert (tg.groupby(["lead", "forecast"]).n.sum().xs("bilinear", level="forecast").values
                == EXPECTED_N).all(), f"by={by} drops station-times"
    assert set(score(S, F, dev, by="hour").hour) == {0, 12}
    done.append("common-valid rows identical across leads; groupings keep every station-time")

    # bootstrap known answers
    Fb = forecasts(S, {"b+1": _pred_file(S, dev, B[dev] + 1.0),
                       "b+5": _pred_file(S, dev, B[dev] + 5.0)})
    for rs in (False, True):
        z = bootstrap(S, Fb, dev, "bilinear", "bilinear", n_boot=300, resample_stations=rs)
        assert (z[["estimate", "lo", "hi"]].values == 0).all(), "self-difference not [0, 0]"
    b1 = bootstrap(S, Fb, dev, "b+1", "bilinear", n_boot=300, seed=3)
    me = b1[b1.metric == "me"]
    # files are float32, so B + 1 is 1 to within a float32 step at ~20 C
    assert np.allclose(me[["estimate", "lo", "hi"]].values, 1.0, rtol=0, atol=2e-6)
    tb = score(S, Fb, dev).set_index(["lead", "forecast"])
    for _, r in b1.iterrows():
        want = tb.loc[(r.lead, "b+1"), r.metric] - tb.loc[(r.lead, "bilinear"), r.metric]
        assert abs(r.estimate - want) < 1e-9, "bootstrap estimate is not the table difference"
        assert r.lo <= r.estimate <= r.hi or r.metric == "me"
    rm = b1[b1.metric == "rmse"].set_index("lead").estimate
    me_b = tb.xs("bilinear", level="forecast").me
    assert (np.sign(rm) == np.sign(2 * me_b.loc[rm.index] + 1)).all(), "+1 C shift: wrong sign"
    b1r = bootstrap(S, Fb, dev, "bilinear", "b+1", n_boot=300, seed=3)
    assert np.allclose(b1r.estimate, -b1.estimate, atol=1e-12)
    assert np.allclose(b1r.lo, -b1.hi, atol=1e-9) and np.allclose(b1r.hi, -b1.lo, atol=1e-9)
    b5 = bootstrap(S, Fb, dev, "b+5", "bilinear", n_boot=300, resample_stations=True)
    assert (b5[b5.metric != "me"].lo > 0).all(), "+5 C shift not worse with certainty"
    idx = _block_days(np.random.default_rng(0), 63, 5, 2000)
    assert idx.shape == (2000, 63) and (np.diff(idx[:, :60].reshape(2000, 12, 5), axis=2) % 63 == 1).all()
    counts = np.stack([np.bincount(i, minlength=63) for i in idx])
    assert np.abs(counts.mean(0) - 1).max() < 0.1, "circular blocks weight the days unevenly"
    days_only = bootstrap(S, Fb, dev, "b+1", "bilinear", n_boot=300, seed=4)
    crossed = bootstrap(S, Fb, dev, "b+1", "bilinear", n_boot=300, seed=4, resample_stations=True)
    w = [(x[x.metric == "rmse"].hi - x[x.metric == "rmse"].lo).values for x in (days_only, crossed)]
    assert (w[1] > w[0]).all(), "resampling stations adds no spread"
    done.append("bootstrap: self [0, 0], +1 C shift ME [1, 1] and sign, antisymmetric, +5 C worse, "
                "circular blocks contiguous and even, stations resampled")

    # too few days at a lead: no interval, never a zero-width one
    days = S["valid"].asi8[l24] // NS_DAY
    for n_days, has in ((5, False), (19, False), (20, True)):
        r = l24[np.isin(days, np.unique(days)[:n_days])]
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            z = bootstrap(S, Fb, r, "b+1", "bilinear", n_boot=200)
        z = z[z.metric != "me"]
        assert z.lo.notna().all() == has and z.hi.notna().all() == has, (n_days, z)
        assert has or any("no interval" in str(c.message) for c in caught)
        assert not has or (z.lo < z.hi).all()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        whole = bootstrap(S, Fb, dev, "b+1", "bilinear", n_boot=50, block_days=10_000)
    assert whole[["lo", "hi"]].isna().all().all(), "a block longer than the days present gave an interval"
    done.append("bootstrap: under 4 blocks of days at a lead gives no interval, not a zero-width one")

    # known-truth widths: 62 days x 2 times x 83 stations, ME difference = mean of x. The
    # plain moving block gave 0.94 days only (91-92 % coverage) and 1.68 crossed on noise
    def mean_width(sA, sB, sE, rs, reps=100):
        rng = np.random.default_rng(1)
        K, C = 62, 83
        out = []
        for i in range(reps):
            x = (np.repeat(rng.normal(0, sA, K), 2)[:, None] + rng.normal(0, sB, C)
                 + rng.normal(0, sE, (2 * K, C)))
            obs = rng.normal(15, 5, (2 * K, C))
            Fx = {"A": _fc("point", obs + x), "B": _fc("point", obs)}
            z = bootstrap(_synthetic(obs), Fx, np.arange(2 * K), "A", "B", n_boot=500,
                          resample_stations=rs, seed=i)
            out.append(float(np.diff(z.loc[z.metric == "me", ["lo", "hi"]].values[0])[0]))
        true_sd = np.sqrt(sA ** 2 / K + sE ** 2 / (2 * K * C) + (sB ** 2 / C if rs else 0))
        return np.mean(out) / (2 * norm.ppf(0.975) * true_sd)
    ratios = [mean_width(0, 0, 1, False), mean_width(0, 0, 1, True),
              mean_width(0.0204, 0.143, 0.412, True)]
    assert 0.99 < ratios[0] < 1.12, f"days-only width / true 95 % width {ratios[0]:.3f}"
    assert 0.99 < ratios[1] < 1.2, f"crossed, noise only: width / true {ratios[1]:.3f}"
    assert 0.95 < ratios[2] < 1.1, f"crossed, day + station + noise: width / true {ratios[2]:.3f}"
    done.append("bootstrap widths on known truth: days only {:.2f}, crossed noise only {:.2f}, "
                "crossed with station effects {:.2f} x the true 95 % width".format(*ratios))

    # temporal folds that disagree, known truth 0: 3 folds x 21 days x 2 times x 83 stations,
    # x = fold step N(0, tau^2) + day N(0, 0.05^2) + N(0, 0.4^2). The same data with the fold
    # labels hidden is what 5-day blocks alone give
    def fold_cover(tau, reps=150):
        rng = np.random.default_rng(11)
        K, C = 63, 83
        fold = np.repeat(np.arange(3), 2 * K // 3)
        hits, width = np.zeros(2), np.zeros(2)
        for i in range(reps):
            x = ((rng.normal(0, tau, 3)[fold] + np.repeat(rng.normal(0, 0.05, K), 2))[:, None]
                 + rng.normal(0, 0.4, (2 * K, C)))
            obs = rng.normal(15, 5, (2 * K, C))
            Fx = {"A": _fc("point", obs + x), "B": _fc("point", obs)}
            syn = _synthetic(obs, fold=fold)
            for j, s in enumerate((syn, dict(syn, fold=np.zeros_like(fold)))):
                z = bootstrap(s, Fx, np.arange(2 * K), "A", "B", n_boot=300, seed=i)
                lo, hi = z.loc[z.metric == "me", ["lo", "hi"]].values[0]
                hits[j] += lo <= 0 <= hi
                width[j] += hi - lo
        return hits / reps, width[0] / width[1]
    (step, hidden), _ = fold_cover(0.1)
    assert step >= 0.87 and hidden <= 0.7, f"fold step: coverage {step:.2f}, folds hidden {hidden:.2f}"
    (flat, _), wr = fold_cover(0.0)
    assert 0.91 <= flat <= 0.99 and wr <= 1.3, f"no fold effect: coverage {flat:.2f}, width x {wr:.2f}"

    # the dev rows: a lookup (bilinear + mean residual per cell, lead and hour, fitted on the
    # other dev folds) has an ME difference against bilinear that moves by fold. Its interval
    # holds every fold's own estimate; 5-day blocks alone (fold labels hidden) miss two of
    # the three at every lead
    look = np.empty(M0.shape, "float32")
    for k in DEV_FOLDS:
        for L in LEADS:
            for h in (0, 12):
                fit = ((S["lead"] == L) & (S["hour"] == h) & np.isin(S["fold"], DEV_FOLDS)
                       & (S["fold"] != k))
                sel = (ld == L) & (ho == h) & (fo == k)
                look[sel] = B[dev[sel]] + S["d"]["R"][fit].mean(0)
    Fl = forecasts(S, {"look": _pred_file(S, dev, look)})
    bl = bootstrap(S, Fl, dev, "look dressed", "bilinear dressed", n_boot=300).set_index(["lead", "metric"])
    hid = bootstrap(dict(S, fold=np.zeros_like(S["fold"])), Fl, dev, "look dressed", "bilinear dressed",
                    n_boot=300).set_index(["lead", "metric"])
    tf = score(S, Fl, dev, by="tfold").pivot_table(index=["lead", "tfold"], columns="forecast", values="me")
    per_fold = tf["look dressed"] - tf["bilinear dressed"]
    for L in LEADS:
        r, h, e = bl.loc[(L, "me")], hid.loc[(L, "me")], per_fold.loc[L]
        assert r.folds == 3 and r.fold_share > 0.5, (L, r)
        assert r.lo <= e.min() and e.max() <= r.hi, f"+{L} h: [{r.lo:.3f}, {r.hi:.3f}] misses a fold {e.values}"
        assert ((e < h.lo) | (e > h.hi)).sum() >= 1, f"+{L} h: folds agree, the check proves nothing"
    done.append(f"bootstrap with disagreeing folds: fold-step coverage {step:.2f} (folds hidden "
                f"{hidden:.2f}), {flat:.2f} without a fold effect (width x {wr:.2f}); a fold-fitted "
                "lookup's ME interval holds every fold's estimate at every lead")
    return done


# ---------------------------------------------------------------- CLI

def _parse_pred(s):
    """--pred [NAME=]FILE -> (name, path). NAME is the text before the first '=' when it is
    not empty and holds no '/'; otherwise, or when only the whole argument names a file,
    the whole argument is the path (so run/lr=0.002/model.npz works). The name defaults to
    the file's stem; ./lr=0.002/model.npz forces a path whose first directory has '='."""
    name, eq, path = s.partition("=")
    if not eq or not name or "/" in name or (Path(s).is_file() and not Path(path).is_file()):
        name, path = "", s
    return (name or Path(path).stem), path


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0].strip(),
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--check", action="store_true", help="run the self-check and exit")
    p.add_argument("--pred", action="append", default=[], metavar="[NAME=]FILE",
                   help="a model's prediction file (.npz); repeatable. NAME defaults to the file "
                        "stem, must be unique and holds no '/'; a path may contain '='")
    p.add_argument("--folds", type=int, nargs="+", default=list(DEV_FOLDS),
                   help="temporal folds to score (default: dev folds 0 1 2)")
    p.add_argument("--unlock-test", action="store_true",
                   help="allow folds 3-12, the sealed confirmatory test: only for a frozen model")
    p.add_argument("--by", nargs="+", default=[], choices=GROUPINGS,
                   help="split each lead's table by valid hour, station fold or temporal fold "
                        "(the bootstrap stays per lead)")
    p.add_argument("--common-valid", action="store_true",
                   help="score only (station, valid) pairs present at every lead")
    p.add_argument("--intersect", action="store_true",
                   help="score every forecast on the rows all prediction files cover")
    p.add_argument("--pair", nargs=2, action="append", metavar=("A", "B"),
                   help="bootstrap A - B (repeatable; default: each dressed model and "
                        "bilinear dressed against AIFS ENS, each dressed model against bilinear dressed)")
    p.add_argument("--n-boot", type=int, default=2000)
    p.add_argument("--block-days", type=int, default=BOOT_BLOCK_DAYS)
    p.add_argument("--resample-stations", action="store_true",
                   help="bootstrap also redraws stations with replacement, crossed with the days "
                        "(the crossed resample's double-counted station-time noise is removed)")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--no-tracking-check", action="store_true",
                   help="accept prediction fields that do not track their own valid time")
    p.add_argument("--out", type=Path, help="write tables and bootstrap (.md, .csv) here")
    p.add_argument("--figure", action="store_true",
                   help="with --out: CRPS by lead on valid times shared by all leads (matplotlib)")
    a = p.parse_args(argv)
    if a.check:
        print("\n".join(["self_check passed:"] + ["  " + s for s in self_check()]))
        return
    sealed = sorted(set(a.folds) - set(DEV_FOLDS))
    if sealed and not a.unlock_test:
        p.error(f"folds {sealed} are the sealed confirmatory test; --unlock-test only for a frozen model")
    if a.figure and a.out is None:
        p.error("--figure needs --out")
    if a.block_days < 1:
        p.error("--block-days must be >= 1")
    preds = {}
    for s in a.pred:
        name, path = _parse_pred(s)
        if name in preds:
            p.error(f"--pred name {name!r} repeats ({preds[name]}, {path}); name each file: "
                    "--pred NAME=FILE")
        if not Path(path).is_file():
            p.error(f"--pred {s!r}: no file {path!r}")
        preds[name] = path

    S = load()
    try:
        F = forecasts(S, preds, check_tracking=not a.no_tracking_check)
    except ValueError as e:
        p.error(str(e))
    rows = select_rows(S, folds=a.folds, unlock_test=a.unlock_test)
    kw = dict(unlock_test=a.unlock_test, intersect=a.intersect)
    t = score(S, F, rows, by=a.by, common_valid=a.common_valid, **kw)

    pairs = a.pair or ([(f"{m} dressed", "AIFS ENS") for m in preds]
                       + [("bilinear dressed", "AIFS ENS")]
                       + [(f"{m} dressed", "bilinear dressed") for m in preds])
    unknown = sorted({x for pair in pairs for x in pair} - set(F))
    if unknown:
        p.error(f"--pair names {unknown} are not forecasts; they are: {', '.join(F)}")
    bs = pd.concat([bootstrap(S, F, rows, x, y, n_boot=a.n_boot, block_days=a.block_days,
                              resample_stations=a.resample_stations, seed=a.seed,
                              common_valid=a.common_valid, **kw) for x, y in pairs],
                   ignore_index=True).sort_values("lead", kind="stable")

    v = S["valid"][np.unique(_station_times(S, F, rows, common_valid=a.common_valid, **kw)[0]["row"])]
    note = (f"Comparison B: {len(S['st'])} scored SYNOP stations, temporal folds "
            f"{' '.join(map(str, a.folds))}, valid {v.min():%Y-%m-%d} to {v.max():%Y-%m-%d}"
            f"{', valid times shared by all leads' if a.common_valid else ''}"
            f"{', rows all prediction files cover' if a.intersect else ''}. "
            "ME = forecast - obs; a point row's CRPS is its MAE; dressed = N(mean, AIFS spread "
            "at the 0.25 deg cell); spread/RMSE = sqrt(mean(s^2)(M+1)/M)/RMSE with s^2 the unbiased "
            f"member variance (stored spread^2 x M/(M-1)), M = {M_MEMBERS}.")
    bnote = (f"Circular moving-block bootstrap, {a.n_boot} replicates, blocks of {a.block_days} valid "
             f"days, stations kept together{' and resampled (crossed)' if a.resample_stations else ''}, "
             f"seed {a.seed}; 95 % intervals for A - B on the table's station-times, the replicate "
             "spread scaled for the block bootstrap's small-sample bias. With 3 or more temporal "
             "folds, where the folds disagree by more than the blocks allow, the excess is added "
             "as a between-fold variance and the interval widened; fold share is its part of the "
             "day variance (score_stations.bootstrap). "
             f"Blank: fewer than {BOOT_MIN_BLOCKS * a.block_days} valid days at that lead. "
             "Negative RMSE/CRPS differences favour A.")
    md = tables_md(t, "Station scores per lead", note)
    bmd = bootstrap_md(bs, "Score differences per lead", bnote)
    print(md)
    print(bmd)
    if a.out is not None:
        a.out.mkdir(parents=True, exist_ok=True)
        (a.out / "tables.md").write_text(md)
        t.to_csv(a.out / "tables.csv", index=False, float_format="%.6f")
        (a.out / "bootstrap.md").write_text(bmd)
        bs.to_csv(a.out / "bootstrap.csv", index=False, float_format="%.6f")
        if a.figure:
            # the figure compares leads, so it keeps the valid times every lead shares
            tc = score(S, F, rows, common_valid=True, **kw)
            dc = pd.concat([bootstrap(S, F, rows, n, "AIFS ENS", n_boot=a.n_boot,
                                      block_days=a.block_days, seed=a.seed, common_valid=True,
                                      resample_stations=a.resample_stations, **kw)
                            for n in F if F[n]["kind"] == "dressed" and not n.startswith("CERRA")],
                           ignore_index=True)
            tc.to_csv(a.out / "crps_by_lead.csv", index=False, float_format="%.6f")
            dc.to_csv(a.out / "crps_by_lead_diff.csv", index=False, float_format="%.6f")
            sub = (f"Comparison B, temporal folds {' '.join(map(str, a.folds))}, valid times shared "
                   f"by all leads, n = {int(tc.n.iloc[0])} station-times per lead.\nDressed = N(mean, "
                   f"AIFS spread at the 0.25 deg cell). Bars: 95 % circular moving-block bootstrap intervals "
                   f"({a.block_days}-day blocks{', stations resampled' if a.resample_stations else ''}; "
                   "widened where the temporal folds disagree).")
            plot_crps(tc, dc, a.out / "crps_by_lead.png", sub)


if __name__ == "__main__":
    main()
