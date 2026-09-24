"""
Crop a multi-message CERRA GRIB (e.g. one full year, 2928 messages) to the
Leningrad+100km target window.

  python crop_cerra_multimsg.py <file.grib> [out.zarr]

Why eccodes directly instead of xr.open_dataset(engine="cfgrib"):
cfgrib builds an index over every message before yielding anything, which for a
6.7 GB / 2928-message file costs minutes and a lot of RAM. Iterating messages
with eccodes decodes ONE 1069x1069 field at a time (4.6 MB), crops it to
127x123, and discards it — so peak memory is flat regardless of file size.

CDS does not return messages in chronological order, so times are collected per
message and the stack is sorted at the end.

Crop is by GRID INDEX, never lat/lon slicing: CERRA rows are not
constant-latitude on its Lambert conformal grid.
"""
import json
import os
import sys
import time as _time

import eccodes
import numpy as np
import pandas as pd
import xarray as xr

SPEC = "domain_spec_leningrad.json"
NX_FULL = NY_FULL = 1069


def main():
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "cerra_t2m_leningrad.zarr"

    sp = json.load(open(SPEC))
    i0, i1 = sp["target"]["i_range"]
    j0, j1 = sp["target"]["j_range"]
    nx, ny = sp["target"]["shape_xy"]

    fields, times, lat2d, lon2d = [], [], None, None
    n = 0
    t0 = _time.time()
    with open(src, "rb") as f:
        while True:
            gid = eccodes.codes_grib_new_from_file(f)
            if gid is None:
                break
            try:
                ni = eccodes.codes_get(gid, "Ni")
                nj = eccodes.codes_get(gid, "Nj")
                if (ni, nj) != (NX_FULL, NY_FULL):
                    raise ValueError(f"message {n}: grid {ni}x{nj}, expected "
                                     f"{NX_FULL}x{NY_FULL}")
                sn = eccodes.codes_get(gid, "shortName")
                if sn != "2t":
                    raise ValueError(f"message {n}: shortName={sn}, expected 2t")

                vals = eccodes.codes_get_values(gid).reshape(nj, ni)
                fields.append(vals[j0:j1 + 1, i0:i1 + 1].astype("float32"))

                d = eccodes.codes_get(gid, "dataDate")
                hhmm = eccodes.codes_get(gid, "dataTime")
                times.append(pd.Timestamp(f"{d:08d}") + pd.Timedelta(hours=hhmm // 100))

                if lat2d is None:      # geometry is identical across messages
                    lat2d = eccodes.codes_get_array(gid, "latitudes").reshape(nj, ni)
                    lon2d = eccodes.codes_get_array(gid, "longitudes").reshape(nj, ni)
                    lat2d = lat2d[j0:j1 + 1, i0:i1 + 1]
                    lon2d = ((lon2d[j0:j1 + 1, i0:i1 + 1] + 180) % 360) - 180
            finally:
                eccodes.codes_release(gid)
            n += 1
            if n % 500 == 0:
                print(f"  {n} messages, {_time.time()-t0:.0f}s", flush=True)

    arr = np.stack(fields)                       # (time, y, x)
    tix = pd.DatetimeIndex(times)
    order = np.argsort(tix.values)
    arr, tix = arr[order], tix[order]
    assert arr.shape[1:] == (ny, nx), f"crop is {arr.shape[1:]}, spec says {(ny, nx)}"
    dup = int(pd.Series(tix).duplicated().sum())

    if arr.mean() > 100:                         # Kelvin -> degC
        arr = arr - 273.15

    ds = xr.Dataset(
        {"t2m": (("time", "y", "x"), arr)},
        coords={"time": tix,
                "latitude": (("y", "x"), lat2d),
                "longitude": (("y", "x"), lon2d)},
        attrs={"source": os.path.basename(src),
               "grid": f"CERRA {NX_FULL}x{NY_FULL} Lambert, cropped",
               "i_range": [i0, i1], "j_range": [j0, j1], "units": "degC"},
    )
    ds.to_zarr(out, mode="w")

    print(f"\nmessages={n} duplicate_times={dup}")
    print(f"shape={dict(ds.sizes)} span={tix.min()} .. {tix.max()}")
    print(f"t2m degC: min {float(arr.min()):.1f} mean {float(arr.mean()):.1f} "
          f"max {float(arr.max()):.1f} | NaNs {int(np.isnan(arr).sum())}")
    print(f"wrote {out} in {_time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
