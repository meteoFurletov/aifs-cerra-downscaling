"""
Training sets, assembled on demand from four source files.

    from dataset import load_stage1, load_stage2, load_sources
    d = load_stage2()          # X, Y, B, R, lead, fold, valid, ...
    d = load_stage2(aux=True)  # + ERA5 lake/snow/skin/wind channels
    d = load_stage1()

Layout
------
One file per source, holding exactly what that source provides and nothing derived:

  cerra.npz          t2m (2680, 123, 127) degC, 3-hourly analyses, + time, lat, lon,
                     orog, lsm                                    <- TARGET, 5.5 km
  era5.npz           t2m (2680, 57, 116) degC + lake_ice_depth, lake_mix_layer_temp_C,
                     lake_cover, snow_depth, skin_temp_C, u10, v10 + time, lat, lon
                                                        <- stage-1 INPUT + predictors
  aifs.npz           cube (667, 6, 3, 57, 116) degC, field = (control, mean, spread),
                     + init_time, lead_h, lat, lon              <- stage-2 INPUT
  stations.parquet   299 x 21 - sid, name, country, lat/lon/elev, role, spatial fold
  station_obs.parquet 717,034 x 3 - sid, time, t2m_obs           <- TRUTH

Everything else is derived here: valid-time pairing, the bilinear baseline B, the
residual R = Y - B, and the fold assignment. Nothing is stored twice, so no two
files can drift out of agreement.

The baseline is the only real compute (~70 s for stage 2). It is cached to
_cache_B_stage{1,2}.npy on first call and reused after.

Conventions this file enforces
-----------------------------
  * Residual target. R = Y - bilinear(input). A model that outputs zero reproduces
    interpolation exactly, so it starts at parity and cannot do worse by accident.
  * Nearest cell for stations, bilinear for fields. Gridded values are grid-box
    averages; interpolating one to a point invents a value the dataset never claimed.
  * FOLD_EPOCH is shared by both stages, so fold k is the same date range in each and
    a model pretrained on stage-1 folds != k can be tested on stage-2 fold k.
  * np.floor for the day index, never astype(int): astype truncates toward zero, so a
    timestamp 21 h before the epoch gives -0.875 -> 0 and lands in fold 0.
"""

import os
from pathlib import Path

import numpy as np
import pandas as pd

# Where the source files live. Defaults to ./data next to this file; override with
# the DOWNSCALING_DATA environment variable. Exported from Claude Science 2026-09-24.
DATA_DIR = Path(os.environ.get("DOWNSCALING_DATA",
                               Path(__file__).resolve().parent / "data"))

FOLD_EPOCH = pd.Timestamp("2025-07-02")
BLOCK_DAYS = 21
GAP_DAYS = 5
AUX_FIELDS = ("lake_ice_depth", "lake_mix_layer_temp_C", "lake_cover",
              "snow_depth", "skin_temp_C", "u10", "v10")
SOURCES = {"cerra": "cerra.npz", "era5": "era5.npz", "aifs": "aifs.npz",
           "stations": "stations.parquet", "obs": "station_obs.parquet"}


def _path(host, filename):
    """Resolve a source file.

    host=None        -> DATA_DIR / filename (the normal, local case)
    host=str or Path -> that directory / filename
    anything else    -> the Claude Science host API, so the file still runs there
    """
    if host is None or isinstance(host, (str, os.PathLike)):
        p = Path(host) / filename if host is not None else DATA_DIR / filename
        if not p.exists():
            raise FileNotFoundError(f"source file not found: {p}")
        return str(p)
    hits = host.artifacts(filename=filename, exact=True)["artifacts"]
    if not hits:
        raise FileNotFoundError(f"artifact not found: {filename}")
    return host.artifact_path(hits[0]["latest_version_id"])


def load_sources(host=None, which=("cerra", "era5", "aifs")):
    """Raw source arrays, nothing derived."""
    S = {}
    for k in which:
        fn = SOURCES[k]
        S[k] = (pd.read_parquet(_path(host, fn)) if fn.endswith(".parquet")
                else dict(np.load(_path(host, fn))))
    return S


def assign_folds(valid, epoch=FOLD_EPOCH):
    day = np.floor((valid - epoch) / pd.Timedelta(days=1)).astype(int)
    period = BLOCK_DAYS + GAP_DAYS
    return day // period, (day % period >= BLOCK_DAYS) | (day < 0)


def _bilinear(fields, src_lat, src_lon, tgt_lat, tgt_lon):
    """Coarse -> target grid. Cell centres, so bilinear; see GRIDS.md 4a."""
    from scipy.interpolate import RegularGridInterpolator
    pts = np.column_stack([tgt_lat.ravel(), tgt_lon.ravel()])
    B = np.empty((len(fields),) + tgt_lat.shape, "float32")
    for k in range(len(fields)):
        f = RegularGridInterpolator((src_lat[::-1], src_lon), fields[k][::-1],
                                    bounds_error=False, fill_value=None)
        B[k] = f(pts).reshape(tgt_lat.shape)
    return B


def _cached_baseline(tag, fields, src_lat, src_lon, tgt_lat, tgt_lon):
    (DATA_DIR / "cache").mkdir(parents=True, exist_ok=True)
    cache = DATA_DIR / "cache" / f"_cache_B_{tag}.npy"
    if os.path.exists(cache):
        B = np.load(cache)
        if B.shape == (len(fields),) + tgt_lat.shape:
            return B
    B = _bilinear(fields, src_lat, src_lon, tgt_lat, tgt_lon)
    np.save(cache, B)
    return B


def _attach_aux(d, era5, times):
    idx = {t: i for i, t in enumerate(pd.to_datetime(era5["time"], unit="s"))}
    take = np.array([idx[t] for t in times])
    d["aux"] = np.stack([era5[f][take] for f in AUX_FIELDS], axis=1)
    d["aux_names"] = list(AUX_FIELDS)
    return d


def load_stage2(host=None, aux=False, leads=None):
    """AIFS forecast -> CERRA analysis. The input carries real forecast error."""
    S = load_sources(host, ("cerra", "aifs") + (("era5",) if aux else ()))
    cer, aif = S["cerra"], S["aifs"]
    ct = pd.to_datetime(cer["time"], unit="s")
    it = pd.to_datetime(aif["init_time"], unit="s")
    lh = aif["lead_h"].astype(int)
    if leads is not None:
        keep_l = np.isin(lh, leads)
        aif = {**aif, "cube": aif["cube"][:, keep_l]}
        lh = lh[keep_l]
    cidx = {t: i for i, t in enumerate(ct)}

    rows = []
    for i, t0 in enumerate(it):
        for j, L in enumerate(lh):
            vt = t0 + pd.Timedelta(hours=int(L))
            if vt in cidx:
                rows.append((i, j, int(L), vt, cidx[vt]))
    if not rows:
        raise ValueError("no AIFS lead lands on a CERRA analysis time")
    ai = np.array([r[0] for r in rows]); aj = np.array([r[1] for r in rows])
    lead = np.array([r[2] for r in rows], "int32")
    valid = pd.DatetimeIndex([r[3] for r in rows])
    ci = np.array([r[4] for r in rows])

    fold, in_gap = assign_folds(valid)
    keep = ~in_gap
    ai, aj, lead, valid, ci, fold = (ai[keep], aj[keep], lead[keep],
                                     valid[keep], ci[keep], fold[keep])
    X = aif["cube"][ai, aj]                       # (n, 3, 57, 116)
    Y = cer["t2m"][ci]                            # (n, 123, 127)
    B = _cached_baseline("stage2", X[:, 1], aif["lat"], aif["lon"],
                         cer["lat"], cer["lon"])
    d = dict(X=X, Y=Y, B=B, R=(Y - B).astype("float32"), lead=lead, fold=fold,
             valid=valid, doy=valid.dayofyear.values,
             orog=cer["orog"], lsm=cer["lsm"],
             tgt_lat=cer["lat"], tgt_lon=cer["lon"],
             src_lat=aif["lat"], src_lon=aif["lon"])
    return _attach_aux(d, S["era5"], valid) if aux else d


def load_stage1(host=None, aux=False, three_channel=True):
    """ERA5 analysis -> CERRA analysis. No forecast error; the pure spatial operator.

    three_channel repeats the analysis into (control, mean, spread=0) so the
    stage-2 architecture consumes stage-1 data unchanged.
    """
    S = load_sources(host, ("cerra", "era5"))
    cer, er = S["cerra"], S["era5"]
    ct = pd.to_datetime(cer["time"], unit="s")
    et = pd.to_datetime(er["time"], unit="s")
    common = et.intersection(ct)
    ei = np.array([{t: i for i, t in enumerate(et)}[t] for t in common])
    ci = np.array([{t: i for i, t in enumerate(ct)}[t] for t in common])

    fold, in_gap = assign_folds(common)
    keep = ~in_gap
    ei, ci, fold, valid = ei[keep], ci[keep], fold[keep], common[keep]
    x1 = er["t2m"][ei][:, None]                   # (n, 1, 57, 116)
    X = (np.concatenate([x1, x1, np.zeros_like(x1)], 1) if three_channel else x1)
    Y = cer["t2m"][ci]
    B = _cached_baseline("stage1", x1[:, 0], er["lat"], er["lon"],
                         cer["lat"], cer["lon"])
    d = dict(X=X.astype("float32"), Y=Y, B=B, R=(Y - B).astype("float32"),
             lead=np.zeros(len(X), "int32"), fold=fold, valid=valid,
             doy=valid.dayofyear.values, orog=cer["orog"], lsm=cer["lsm"],
             tgt_lat=cer["lat"], tgt_lon=cer["lon"],
             src_lat=er["lat"], src_lon=er["lon"])
    return _attach_aux(d, er, valid) if aux else d


def load_stations(host=None):
    """Station metadata (with spatial folds) and observations."""
    S = load_sources(host, ("stations", "obs"))
    return S["stations"], S["obs"]


def check(host=None):
    """Assert the assembled sets match the documented values."""
    o = {}
    d2 = load_stage2(host)
    o["s2_samples"] = d2["X"].shape[0] == 3240
    o["s2_folds"] = len(np.unique(d2["fold"])) == 13
    o["s2_baseline"] = abs(float(np.sqrt((d2["R"] ** 2).mean())) - 2.0645) < 5e-4
    o["s2_leads"] = sorted(np.unique(d2["lead"]).tolist()) == [0, 24, 48, 72, 120, 168]
    d1 = load_stage1(host)
    o["s1_samples"] = d1["X"].shape[0] == 2184
    o["s1_baseline"] = abs(float(np.sqrt((d1["R"] ** 2).mean())) - 1.2355) < 5e-4
    o["s1_folds_uniform"] = len(set(np.bincount(d1["fold"]).tolist())) == 1
    o["s1_spread_zero"] = not d1["X"][:, 2].any()
    o["grids_match"] = d1["X"].shape[-2:] == d2["X"].shape[-2:]
    o["folds_aligned"] = all(
        d1["valid"][d1["fold"] == k].min().date()
        == d2["valid"][d2["fold"] == k].min().date() for k in range(13))
    o["no_cross_stage_leak"] = 0 == sum(
        int((((d1["valid"][d1["fold"] != k]) >= d2["valid"][d2["fold"] == k].min())
             & ((d1["valid"][d1["fold"] != k]) <= d2["valid"][d2["fold"] == k].max())
             ).sum()) for k in range(13))
    st, ob = load_stations(host)
    o["target_stations"] = int((st.role == "target").sum()) == 85
    o["scored_stations"] = int(st.scored.sum()) == 83
    o["obs_rows"] = len(ob) == 717034
    o["sid_zeros_kept"] = bool(st.sid.str.startswith("0").any())
    return o
