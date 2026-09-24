"""
Build the stage-1 training set: ERA5 analysis -> CERRA analysis, same valid time.

  python pair_era5_cerra.py era5_2025H2.grib era5_2026H1.grib [out.npz]

Inputs   era5_*.grib            0.25 deg, area-subset to the stage-2 input grid
         cerra_target.npz       (2680, 123, 127) target series + times
         cerra_static_target.npz
Output   stage1_pairs.npz       X (n, 1, 57, 116), Y/B/R (n, 123, 127), + fold/valid

Why stage 1 exists
------------------
Both sides are ANALYSES, so the input carries no forecast error. The model learns
the pure spatial question - given a coarse field, where does fine structure go -
without also having to cope with a displaced front. Stage 2 then fine-tunes on
AIFS->CERRA pairs where the input does carry forecast error.

The order matters and is not interchangeable. A model trained ONLY on stage-2
pairs has too few samples to learn the operator across a seasonal cycle. A model
trained ONLY on stage 1 has learned that its input is essentially correct, and
will sharpen a displaced front confidently - producing a crisp field that is as
wrong as the blurry one, and arguably worse because sharpness reads as skill.

Three things that must match stage 2 exactly, or the stages cannot share a model
----------------------------------------------------------------------------------
  * THE INPUT GRID. ERA5 is requested with area=[67.0, 18.5, 53.0, 47.25], which
    reproduces the stage-2 input grid's 57 x 116 exactly. Asserted below against
    src_lat/src_lon stored in stage2_pairs.npz - not assumed.
  * THE BASELINE. B = bilinear(X) on the CERRA target grid, via the same
    fractional-index sampling as stage 2 (GRIDS.md 4a). R = Y - B is the target,
    so a zero-output model reproduces interpolation exactly.
  * CHANNEL COUNT DIFFERS ON PURPOSE. Stage 2 has 3 input channels (control,
    ensemble mean, spread); an analysis has 1. Train stage 1 on the mean channel
    alone and copy those weights into the stage-2 mean channel, or give stage 1 a
    3-channel input with the analysis repeated and the spread set to zero. The
    second is simpler and is what write_stage2_compatible() below does.

Folds
-----
Stage-1 samples are 3-hourly analyses, so consecutive samples are far MORE
correlated than stage-2's (which are 6 h apart at minimum). The same 21-day
block / 5-day gap scheme is used, giving the same 13 folds on the same calendar
boundaries - so a fold index means the same date range in both stages and a
sample cannot leak between them.
"""

import sys

import numpy as np
import pandas as pd
import xarray as xr

BLOCK_DAYS = 21
GAP_DAYS = 5

# Fold epoch, shared with stage 2 ON PURPOSE. Stage 2's folds are anchored on its
# first AIFS init (2025-07-02); stage 1's natural anchor would be its first CERRA
# analysis (2025-07-01), one day earlier. That one-day offset happens to leak zero
# samples because the 5-day gap absorbs it - but it only works while GAP_DAYS > 1,
# which is a silent dependency. Pinning the epoch makes fold k the same date range
# in both stages by construction, so a model pretrained on stage-1 folds != k can
# be fine-tuned and tested on stage-2 fold k with no overlap to verify.
FOLD_EPOCH = pd.Timestamp("2025-07-02")


def load_era5(paths):
    ds = xr.concat(
        [xr.open_dataset(p, engine="cfgrib", backend_kwargs={"indexpath": ""})
         for p in paths], dim="time").sortby("time")
    v = list(ds.data_vars)[0]
    da = ds[v]
    if "valid_time" in da.coords:          # duplicates 'time' for step=0 analyses
        da = da.drop_vars("valid_time")
    vals = da.values
    if float(np.nanmean(vals)) > 100.0:    # Kelvin -> degC; AIFS is already degC
        vals = vals - 273.15
    return vals.astype("float32"), pd.DatetimeIndex(ds.time.values), \
        ds.latitude.values, ds.longitude.values


def assign_folds(valid, epoch=FOLD_EPOCH):
    # np.floor, NOT astype(int): astype truncates toward zero, so a timestamp
    # 21 hours BEFORE the epoch gives -0.875 -> 0 and lands in fold 0 instead of
    # being dropped. That silently put 7 pre-epoch analyses in fold 0.
    day = np.floor((valid - epoch) / pd.Timedelta(days=1)).astype(int)
    period = BLOCK_DAYS + GAP_DAYS
    fold = day // period
    in_gap = (day % period) >= BLOCK_DAYS
    # samples before the epoch would land in fold -1; drop them with the gaps
    return fold, in_gap | (day < 0)


def main(paths, out="stage1_pairs.npz"):
    from scipy.interpolate import RegularGridInterpolator

    e5, et, elat, elon = load_era5(paths)
    print(f"ERA5: {e5.shape} | {et.min()} .. {et.max()}", flush=True)

    tz = np.load("cerra_target.npz")
    cer, ct = tz["t2m"], pd.to_datetime(tz["time"], unit="s")
    tlat, tlon = tz["tlat"], tz["tlon"]

    # grid identity against stage 2 - assert, do not assume
    s2 = np.load("stage2_pairs.npz")
    sl, so = s2["src_lat"], s2["src_lon"]
    assert e5.shape[-2:] == (len(sl), len(so)), (e5.shape, len(sl), len(so))
    assert np.allclose(elat, sl, atol=1e-6), "ERA5 lat grid differs from stage 2"
    assert np.allclose(elon % 360, so % 360, atol=1e-6), "ERA5 lon grid differs"
    print(f"input grid identical to stage 2: {len(sl)} x {len(so)}", flush=True)

    # pair on exact valid time
    common = et.intersection(ct)
    print(f"common valid times: {len(common):,} of {len(ct):,} CERRA analyses", flush=True)
    ie = {t: i for i, t in enumerate(et)}
    ic = {t: i for i, t in enumerate(ct)}
    X = np.stack([e5[ie[t]] for t in common])[:, None]        # (n, 1, ny, nx)
    Y = np.stack([cer[ic[t]] for t in common])

    # baseline: same fractional-index bilinear as stage 2
    pts = np.column_stack([tlat.ravel(), tlon.ravel()])
    B = np.empty_like(Y)
    for k in range(len(X)):
        f = RegularGridInterpolator((sl[::-1], so), X[k, 0][::-1],
                                    bounds_error=False, fill_value=None)
        B[k] = f(pts).reshape(tlat.shape)
    R = Y - B

    fold, in_gap = assign_folds(common)
    keep = ~in_gap
    print(f"kept {keep.sum():,} of {len(common):,} "
          f"({100*(~keep).mean():.1f}% discarded to fold gaps)", flush=True)
    X, Y, B, R = X[keep], Y[keep], B[keep], R[keep]
    fold, vk = fold[keep], common[keep]

    np.savez_compressed(
        out, X=X, Y=Y, B=B.astype("float32"), R=R.astype("float32"),
        lead_h=np.zeros(len(X), "int32"),      # analyses: lead is 0 by definition
        fold=fold.astype("int32"),
        valid=(vk.values.astype("datetime64[s]").astype("int64")),
        tlat=tlat, tlon=tlon, src_lat=sl, src_lon=so)
    print(f"\n{out}: X {X.shape} Y {Y.shape}", flush=True)
    print(f"  folds {len(np.unique(fold))} | sizes "
          f"{np.bincount(fold.astype(int)).tolist()}", flush=True)
    print(f"  baseline RMSE {np.sqrt((R**2).mean()):.4f} C | residual sd {R.std():.4f}",
          flush=True)
    print(f"  NaNs X {int(np.isnan(X).sum())} Y {int(np.isnan(Y).sum())}", flush=True)
    return X, Y, B, R, fold, vk


def write_stage2_compatible(inp="stage1_pairs.npz", out="stage1_pairs_3ch.npz"):
    """Repeat the analysis into 3 channels with zero spread, so the stage-2
    architecture consumes stage-1 data unchanged."""
    z = np.load(inp)
    X1 = z["X"]
    X3 = np.concatenate([X1, X1, np.zeros_like(X1)], axis=1)   # control, mean, spread=0
    d = {k: z[k] for k in z.files}
    d["X"] = X3.astype("float32")
    np.savez_compressed(out, **d)
    print(f"{out}: X {X3.shape} (channel 2 = spread = 0, an analysis has none)")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a.endswith(".grib")]
    o = [a for a in sys.argv[1:] if a.endswith(".npz")]
    main(args, o[0] if o else "stage1_pairs.npz")
