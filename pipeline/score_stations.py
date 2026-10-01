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
spread/RMSE = sqrt(mean(sd^2) * (M+1)/M) / RMSE with M = 51 members, which is 1 for a
reliable ensemble: its mean misses by (M+1)/M times the member variance.

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
    with its keys, or when under a quarter of its fields sit nearer their own row's
    bilinear field than a neighbouring valid time's (fields written one row off).
  * common_valid=True keeps the (station, valid) pairs scored at every lead only:
    lead 168 starts a week later, so the full tables do not share verification times.
  * Bootstrap intervals are for score differences between two forecasts, per lead:
    moving blocks of 5 valid days over the days present, every station of a drawn day
    kept with it, stations optionally resampled too; 95 % percentile intervals.

Prediction file (.npz; the format of scratch/preds/*.npz)
---------------------------------------------------------
  rows   (n,) int          load_stage2 row indices, checked against the keys
  field  (n, 123, 127)     full 2 m temperature on the target window, degC
  valid  (n,) int64        valid time, ns since the epoch (datetime64 accepted)
  lead   (n,) int          lead, hours
"""
import argparse
import contextlib
import io
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dataset import DATA_DIR, FOLD_EPOCH, load_stage2, load_stations  # noqa: E402

LEADS = (0, 24, 48, 72, 120, 168)
DEV_FOLDS = (0, 1, 2)
M_MEMBERS = 51
BOOT_BLOCK_DAYS = 5
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
        mu, cover = load_pred(S, src, check_tracking)
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
    if np.issubdtype(valid.dtype, np.datetime64):
        valid = valid.astype("datetime64[ns]").astype(np.int64)
    n = len(rows)
    if field.shape != (n,) + S["d"]["Y"].shape[1:] or valid.shape != (n,) or lead.shape != (n,):
        raise ValueError(f"shapes disagree: rows {rows.shape}, field {field.shape}, "
                         f"valid {valid.shape}, lead {lead.shape}")
    if not all(np.issubdtype(a.dtype, np.integer) for a in (rows, valid, lead)):
        raise ValueError("rows, valid (ns) and lead must be integers")
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


def _check_tracking(S, r, field, step=3, floor=0.25):
    """Refuse a file whose fields follow neighbouring valid times rather than their own.

    Each field is compared, in pattern (the domain-mean difference removed, so a bias
    does not count), with the bilinear field of its own row and of the rows at the same
    lead 12 and 24 h either side. A model field corrects its own row's bilinear field,
    so most sit nearest that row: CERRA itself 77 % of rows (32 % at +168 h alone), a
    cell x hour x lead lookup 100 %. A file written one row or one day off: under 10 %.
    A guard against gross misalignment, not proof of alignment.
    """
    B = S["d"]["B"][:, ::step, ::step]
    f = np.asarray(field)[:, ::step, ::step]

    def dist(rr, sel):
        return (f[sel] - B[rr]).std((1, 2))

    own = dist(r, np.ones(len(r), bool))
    near = np.full(len(r), np.inf)
    for h in (-24, -12, 12, 24):
        q = _rows_of(S, S["valid"].asi8[r] + h * NS_HOUR, S["lead"][r])
        has = q >= 0
        near[has] = np.minimum(near[has], dist(q[has], has))
    has = np.isfinite(near)
    frac = float((own[has] < near[has]).mean()) if has.any() else 1.0
    if frac < floor:
        raise ValueError(f"only {frac:.0%} of fields sit nearest their own row's bilinear field: "
                         "the file looks misaligned (check_tracking=False overrides)")


# ---------------------------------------------------------------- scoring

def crps_gauss(y, mu, sd):
    """CRPS of N(mu, sd^2) at y, closed form (Gneiting et al. 2005); sd = 0 gives |y - mu|."""
    y, mu, sd = np.broadcast_arrays(*(np.asarray(v, "float64") for v in (y, mu, sd)))
    shape = y.shape
    y, mu, sd = y.ravel(), mu.ravel(), sd.ravel()
    if not (np.isfinite(sd).all() and (sd >= 0).all()):
        raise ValueError("spread must be finite and >= 0")
    out = np.abs(y - mu)
    p = sd > 0
    z = (y[p] - mu[p]) / sd[p]
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
        a["spread_rmse"] = np.sqrt(a["var"] * (M_MEMBERS + 1) / M_MEMBERS) / a.rmse
        out.append(a.reset_index().assign(forecast=name, kind=f["kind"]))
    t = pd.concat(out, ignore_index=True).sort_values(keys, kind="stable", ignore_index=True)
    assert (t.groupby(keys).n.nunique() == 1).all(), "forecasts scored on different station-times"
    return t[keys + ["forecast", "kind", "n", "me", "rmse", "crps", "spread_rmse"]]


# ---------------------------------------------------------------- bootstrap

def _block_days(rng, K, block, n_boot):
    """(n_boot, K) day indices: moving-block resamples of K days, runs of block days."""
    L = min(block, K)
    starts = rng.integers(0, K - L + 1, size=(n_boot, -(-K // L)))
    return (starts[:, :, None] + np.arange(L)).reshape(n_boot, -1)[:, :K]


def bootstrap(S, F, rows, a, b, n_boot=2000, block_days=BOOT_BLOCK_DAYS,
              resample_stations=False, seed=0, level=0.95, **kw):
    """Score differences a - b per lead, with moving-block bootstrap intervals.

    The station-times are those score() uses for the same F and kw, so the estimate is
    the difference of two table rows. Valid days (UTC dates) are drawn in moving blocks
    of block_days consecutive days, taken over the days present in order (a block may
    straddle a fold gap); every station of a drawn day comes with it. resample_stations
    also redraws the stations with replacement, independently of the days.
    Returns lead, a, b, metric (me, rmse, crps), estimate, lo, hi, n, days.
    """
    T, E = _station_times(S, F, rows, **kw)
    rng = np.random.default_rng(seed)
    q = [(1 - level) / 2, (1 + level) / 2]
    n_st = len(S["st"])
    out = []
    for L in np.unique(T["lead"]):
        m = T["lead"] == L
        days, di = np.unique(T["day"][m], return_inverse=True)
        K = len(days)
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
        diff = dict(me=(A["ea"] - A["eb"]) / n,
                    rmse=np.sqrt(A["sa"] / n) - np.sqrt(A["sb"] / n),
                    crps=(A["ca"] - A["cb"]) / n)
        for k, v in diff.items():
            lo, hi = np.quantile(v[1:], q)
            out.append(dict(lead=int(L), a=a, b=b, metric=k, estimate=v[0], lo=lo, hi=hi,
                            n=int(n[0]), days=K))
    return pd.DataFrame(out)


# ---------------------------------------------------------------- output

def _fmt(v, col):
    if pd.isna(v):
        return ""
    if col in ("n", "days", "lead", "hour", "sfold", "tfold"):
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
    cols = ["a", "b", "metric", "estimate", "lo", "hi", "n", "days"]
    heads = ["A", "B", "metric", "A - B", "2.5 %", "97.5 %", "n", "days"]
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
    # synthetic stations: truth drawn from the forecast itself
    rng = np.random.default_rng(7)
    n, k = 2000, 100
    v = pd.DatetimeIndex(FOLD_EPOCH + pd.to_timedelta(np.arange(n) * 12, "h")).as_unit("ns")
    mu, sd, z = rng.normal(size=(n, k)), rng.uniform(0.5, 2.0, (n, k)), rng.standard_normal((n, k))
    syn = dict(valid=v, lead=np.zeros(n, np.int64), fold=np.zeros(n, int), hour=v.hour.values,
               st=pd.DataFrame({"fold": np.zeros(k, int)}), obs=mu + sd * z)
    ts = score(syn, {"g": _fc("ensemble", mu, sd)}, np.arange(n))
    assert abs(ts.crps[0] / (sd.mean() / np.sqrt(np.pi)) - 1) < 0.005    # E CRPS = sd / sqrt(pi)
    syn["obs"] = mu + sd * np.sqrt((M_MEMBERS + 1) / M_MEMBERS) * z     # a reliable 51-member mean
    ts = score(syn, {"g": _fc("ensemble", mu, sd)}, np.arange(n))
    assert abs(ts.spread_rmse[0] - 1) < 0.006, ts.spread_rmse[0]
    done.append("crps and spread/RMSE known answers")

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
    load_pred(S, _pred_file(S, dev, S["d"]["Y"][dev]))         # CERRA, the furthest from B, passes
    done.append("key alignment: shuffled realigned, off-by-one rows/keys/fields refused")

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

    def tripwire():
        raise AssertionError("the CLI passed the fold guard")
    g["load"] = tripwire                     # a broken guard trips here, before any scoring
    try:
        for argv in (["--folds", "3"], ["--folds", "0", "1", "2", "5"]):
            with contextlib.redirect_stderr(io.StringIO()):
                _refused(lambda: main(argv), SystemExit)
    finally:
        g["load"] = real_load
    done.append("sealed folds 3-12 refused (library and CLI)")

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
    idx = _block_days(np.random.default_rng(0), 63, 5, 50)
    assert idx.shape == (50, 63) and (np.diff(idx[:, :60].reshape(50, 12, 5), axis=2) == 1).all()
    whole = bootstrap(S, Fb, dev, "b+1", "bilinear", n_boot=50, block_days=10_000)
    assert np.allclose(whole.lo, whole.estimate, atol=1e-12) and \
        np.allclose(whole.hi, whole.estimate, atol=1e-12), "a block of every day is not the sample"
    spread = bootstrap(S, Fb, dev, "b+1", "bilinear", n_boot=50, block_days=10_000, resample_stations=True)
    spread = spread[spread.metric == "rmse"]
    assert (spread.lo < spread.estimate).all() and (spread.estimate < spread.hi).all(), \
        "resampling stations adds no spread"
    done.append("bootstrap: self [0, 0], +1 C shift ME [1, 1] and sign, antisymmetric, +5 C worse, "
                "blocks contiguous, stations resampled")
    return done


# ---------------------------------------------------------------- CLI

def _parse_pred(s):
    name, _, path = s.rpartition("=")
    return (name or Path(path).stem), path


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0].strip(),
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--check", action="store_true", help="run the self-check and exit")
    p.add_argument("--pred", action="append", default=[], metavar="[NAME=]FILE",
                   help="a model's prediction file (.npz); repeatable")
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
                   help="bootstrap also redraws stations with replacement")
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

    S = load()
    preds = dict(_parse_pred(s) for s in a.pred)
    F = forecasts(S, preds, check_tracking=not a.no_tracking_check)
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
            f"at the 0.25 deg cell); spread/RMSE = sqrt(mean(sd^2)(M+1)/M)/RMSE, M = {M_MEMBERS}.")
    bnote = (f"Moving-block bootstrap, {a.n_boot} replicates, blocks of {a.block_days} valid days, "
             f"stations kept together{' and resampled' if a.resample_stations else ''}, seed {a.seed}; "
             "95 % percentile intervals for A - B on the table's station-times. "
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
                   f"AIFS spread at the 0.25 deg cell). Bars: 95 % moving-block bootstrap intervals "
                   f"({a.block_days}-day blocks{', stations resampled' if a.resample_stations else ''}).")
            plot_crps(tc, dc, a.out / "crps_by_lead.png", sub)


if __name__ == "__main__":
    main()
