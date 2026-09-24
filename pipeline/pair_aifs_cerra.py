"""
Build the stage-2 training set: AIFS forecast -> CERRA analysis, same valid time.

  python pair_aifs_cerra.py [cerra_zarr] [out.npz]

Inputs
  aifs_overlap.npz            667 inits x 6 leads x (control, ens_mean, ens_sd)
                              on the 0.25 deg input crop, 57 x 116
  cerra_t2m_overlap.zarr      CERRA 2m temperature on the 127 x 123 target window
                              (crop_cerra_multimsg.py output for 2025-07..2026-05)

Output
  stage2_pairs.npz
      X        (n, 3, 57, 116)   AIFS control / ens_mean / ens_sd
      Y        (n, 127, 123)     CERRA target at the same valid time
      lead_h   (n,)              forecast lead, a MODEL INPUT (see below)
      init      (n,)             init time, epoch seconds
      valid     (n,)             valid time, epoch seconds
      fold      (n,)             temporal block id for CV (see below)

Three design decisions, and why
-------------------------------

1. LEAD TIME IS A FEATURE, NOT A NUISANCE.
   Measured AIFS error at stations grows 1.24 -> 3.11 C from +0 to +168 h, and
   the error DECOMPOSES: a fixed 1.24 C analysis/representativeness offset that
   does not grow, plus forecast-error growth in quadrature. A model given lead_h
   can learn a lead-dependent correction; one trained on pooled leads must
   average over regimes that differ by 2.5x in error magnitude. Pass lead_h in.

2. ENSEMBLE SPREAD IS AN INPUT CHANNEL.
   Spread grows 0.53 -> 2.75 C with lead and varies spatially. It is the
   forecast's own uncertainty estimate, and it tells the model when to trust the
   ens_mean field. Cheap to carry (same array), so carry it.

3. FOLDS ARE CONTIGUOUS TIME BLOCKS, NOT RANDOM.
   AIFS inits are 12 h apart and forecasts from adjacent inits overlap heavily
   in valid time. Random splitting puts near-duplicate samples in train and test
   and inflates skill. Blocks are 21 days with a 5-day gap at each boundary.

   The gap is MEASURED, not assumed. Autocorrelation of the raw +24 h
   domain-mean field is r = 0.82 even at 21 days - but that is the SEASONAL
   CYCLE (seasonal sd 9.3 C vs weather-anomaly sd 3.6 C), not predictability.
   Two corrections were needed to see the real number: deseasonalise with a
   61-day centred rolling mean, AND work within a single init cycle, because
   00Z/12Z alternation aliases the diurnal cycle into a spurious negative
   half-day lag. Per-cycle weather anomalies then decay cleanly:

       lag      1 d   2 d   3 d   5 d   7 d  10 d  14 d
       00Z    0.87  0.65  0.48  0.32  0.22  0.12 -0.09
       12Z    0.90  0.71  0.55  0.34  0.18  0.06 -0.09

   A 5-day gap puts adjacent folds at r ~ 0.33 on the domain mean, and the model
   is scored on 127x123 FIELDS whose fine-scale structure decorrelates faster
   than the domain mean. 5 days costs 19% of samples; 7 days costs 25% to move
   r from 0.33 to 0.20. With only ~3,000 samples that trade is not worth it.

   NOTE this is a TEMPORAL split, which is correct HERE and would be wrong for
   station verification. Stage-2's loss is against CERRA, a gridded target that
   does not assimilate our held-out stations differently by date - so temporal
   blocking is the right control for autocorrelation. Station verification still
   requires the SPATIAL holdout from pair_stations_cerra.py, because both ERA5
   and CERRA assimilate the station network.

Spatial alignment: the AIFS crop (0.25 deg) and CERRA target (5.5 km Lambert)
are different grids on purpose - that IS the downscaling task. No regridding is
done here; the model consumes the coarse grid and emits the fine one. The two
windows were defined so the input crop contains the target with >= 300 km of
advection margin on every side.
"""
import json
import os
import sys

import numpy as np
import pandas as pd
import xarray as xr

BLOCK_DAYS = 21
GAP_DAYS = 5      # measured, not guessed - see the autocorrelation note below


def main():
    czarr = sys.argv[1] if len(sys.argv) > 1 else "cerra_t2m_overlap.zarr"
    out = sys.argv[2] if len(sys.argv) > 2 else "stage2_pairs.npz"
    if not os.path.exists(czarr):
        sys.exit(f"{czarr} not found - run crop_cerra_multimsg.py on the "
                 f"2025-07..2026-05 GRIBs first")

    z = np.load("aifs_overlap.npz")
    cube, ti = z["cube"], pd.to_datetime(z["init_time"], unit="s")
    leads = z["lead_h"]
    cer = xr.open_zarr(czarr)
    cvar = [v for v in cer.data_vars][0]
    ct = pd.DatetimeIndex(cer.time.values)
    print(f"AIFS  {cube.shape} | {len(ti)} inits {ti.min()} .. {ti.max()}")
    print(f"CERRA {dict(cer.sizes)} | {len(ct)} times {ct.min()} .. {ct.max()}")

    # every (init, lead) whose valid time exists in CERRA
    rows = []
    cpos = {t: i for i, t in enumerate(ct)}
    for li, L in enumerate(leads):
        vt = ti + pd.Timedelta(hours=int(L))
        for ii, v in enumerate(vt):
            k = cpos.get(v)
            if k is not None:
                rows.append((ii, li, k, int(L), ti[ii].value // 10**9, v.value // 10**9))
    if not rows:
        sys.exit("no (init, lead) pair matched a CERRA time - check the CERRA span")
    R = np.array(rows, dtype="int64")
    print(f"\npaired samples: {len(R):,}")
    per_lead = pd.Series(R[:, 3]).value_counts().sort_index()
    print("per lead:", per_lead.to_dict())

    X = cube[R[:, 0], R[:, 1]].astype("float32")            # (n, 3, lat, lon)
    Y = cer[cvar].values[R[:, 2]].astype("float32")         # (n, y, x)
    valid = pd.to_datetime(R[:, 5], unit="s")

    # contiguous temporal blocks, discarding a gap at each boundary
    day = (valid - valid.min()).days.values
    blk = day // (BLOCK_DAYS + GAP_DAYS)
    within = day % (BLOCK_DAYS + GAP_DAYS)
    keep = within < BLOCK_DAYS
    print(f"\nfold blocks: {blk.max()+1} | discarded to gaps: "
          f"{int((~keep).sum()):,} of {len(keep):,} ({(~keep).mean():.1%})")

    X, Y, R, blk = X[keep], Y[keep], R[keep], blk[keep]
    np.savez_compressed(out, X=X, Y=Y, lead_h=R[:, 3], init=R[:, 4],
                        valid=R[:, 5], fold=blk)
    print(f"\n{out}: X {X.shape} Y {Y.shape} | {os.path.getsize(out)/1e6:.0f} MB")
    print(f"X degC {X[:, :2].min():.1f} .. {X[:, :2].max():.1f} | "
          f"Y degC {Y.min():.1f} .. {Y.max():.1f}")
    print(f"NaNs: X {int(np.isnan(X).sum())} Y {int(np.isnan(Y).sum())}")
    print("fold sizes:", pd.Series(blk).value_counts().sort_index().to_dict())

    # the number any model must beat: interpolated AIFS vs CERRA is not
    # computable here (different grids), so report the naive scale instead
    print(f"\nY spatial sd (per sample, mean): {Y.std(axis=(1, 2)).mean():.3f} C")
    print(f"Y - X[ens_mean] domain-mean offset: "
          f"{(Y.mean(axis=(1, 2)) - X[:, 1].mean(axis=(1, 2))).mean():+.3f} C")


if __name__ == "__main__":
    main()
