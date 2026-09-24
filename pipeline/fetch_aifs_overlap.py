"""
Extract AIFS ENS over the Leningrad input crop for the CERRA-overlap period.

  python fetch_aifs_overlap.py [cycles] [max_inits]
      cycles     comma list of init hours, default "0,12"
      max_inits  stop after N inits (for testing), default all

Why the loop is per-init and reduces immediately
------------------------------------------------
The dynamical.org store is chunked (1, 61, 51, 32, 32) = one chunk holds ALL 61
lead times and ALL 51 members for a 32x32 spatial tile. Consequences, measured:

  * selecting one member costs the SAME as reading all 51 (~25-40 s per init)
  * selecting 5 leads costs the same as all 61
  * the only real cost driver is the number of INITS x spatial tiles

So: read each init exactly once, keep every lead we want, and collapse the
member axis to (control, mean, sd) on the spot. Storing the raw cube would be
~1.1 TB for the overlap; the reduction is ~0.5 MB per init.

Member 0 is the unperturbed CONTROL: verified rank-1 closest to the ensemble
centroid in 16 of 16 inits, 12.5x closer than the perturbed mean.

Units: this store serves temperature_2m in degree_Celsius already. Do NOT
subtract 273.15. (ERA5 from ARCO is Kelvin - that one does need converting.)

Resumable: appends to aifs_overlap.npz via a per-init .npy spool directory, so a
proxy drop costs only the init in flight.
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd
import xarray as xr

SPOOL = "aifs_spool"
OUT = "aifs_overlap.npz"
LEADS_H = [0, 24, 48, 72, 120, 168]
OV_START, OV_END = "2025-07-02", "2026-05-31"


def main():
    import glob
    hits = glob.glob(os.path.expanduser(
        "~/.claude-science/orgs/*/skills/aifs-improver-postproc"))
    if not hits:
        sys.exit("aifs-improver-postproc skill dir not found")
    sys.path.insert(0, hits[0])
    from kernel import open_aifs_ens, retry
    ds_aifs = retry(lambda: open_aifs_ens())
    cycles = [int(c) for c in (sys.argv[1] if len(sys.argv) > 1 else "0,12").split(",")]
    max_inits = int(sys.argv[2]) if len(sys.argv) > 2 else None

    sp = json.load(open("domain_spec_leningrad.json"))
    lo0, la0, lo1, la1 = sp["input_crop"]["bbox_latlon"]

    it = pd.DatetimeIndex(ds_aifs.init_time.values)
    sel = it[(it >= OV_START) & (it <= OV_END) & it.hour.isin(cycles)]
    if max_inits:
        sel = sel[:max_inits]
    os.makedirs(SPOOL, exist_ok=True)
    leads = [np.timedelta64(h, "h") for h in LEADS_H]

    print(f"{len(sel)} inits, cycles {cycles}, leads {LEADS_H}", flush=True)
    t0, done = time.time(), 0
    for k, t in enumerate(sel):
        tag = t.strftime("%Y%m%d%H")
        path = os.path.join(SPOOL, f"{tag}.npy")
        if os.path.exists(path):
            continue
        try:
            a = retry(lambda: ds_aifs["temperature_2m"]
                      .sel(init_time=t, lead_time=leads)
                      .sel(latitude=slice(la1, la0), longitude=slice(lo0, lo1))
                      .compute().values)              # (lead, member, lat, lon)
        except Exception as e:
            print(f"  {tag} FAILED {type(e).__name__} {str(e)[:70]}", flush=True)
            continue
        # collapse members -> (control, mean, sd), keeping every lead
        red = np.stack([a[:, 0], a.mean(axis=1), a.std(axis=1)], axis=1)  # (lead,3,lat,lon)
        np.save(path, red.astype("float32"))
        done += 1
        if done % 10 == 0:
            el = time.time() - t0
            print(f"  {k+1}/{len(sel)} inits | {el/done:.1f} s/init | "
                  f"eta {(len(sel)-k-1)*el/done/3600:.1f} h", flush=True)

    files = sorted(f for f in os.listdir(SPOOL) if f.endswith(".npy"))
    if not files:
        sys.exit("no inits extracted")
    cube = np.stack([np.load(os.path.join(SPOOL, f)) for f in files])
    times = pd.to_datetime([f[:-4] for f in files], format="%Y%m%d%H")
    np.savez_compressed(
        OUT, cube=cube,
        init_time=times.values.astype("datetime64[s]").astype("int64"),
        lead_h=np.array(LEADS_H),
        field=np.array(["control", "ens_mean", "ens_sd"]),
    )
    print(f"\n{OUT}: cube {cube.shape} (init, lead, field, lat, lon) "
          f"= {cube.nbytes/1e6:.0f} MB raw", flush=True)
    print(f"inits {times.min()} .. {times.max()} | "
          f"degC range {cube[:, :, :2].min():.1f} .. {cube[:, :, :2].max():.1f}", flush=True)


if __name__ == "__main__":
    main()
