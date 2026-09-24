"""
Crop downloaded CERRA GRIB files to the Leningrad+100km target window.

Use this when the GRIBs were fetched OUTSIDE this sandbox (e.g. via the CDS web
interface), which is the recommended route: CDS queue time is ~21 s even for a
full year, but sustained byte transfer from here proved unreliable.

  python crop_cerra_grib.py /path/to/gribs [--delete-source]

Reads the target index window from domain_spec_leningrad.json, so the crop stays
consistent with the rest of the project. CERRA is on a 1069x1069 Lambert
conformal grid: crop by GRID INDEX, never by lat/lon slicing -- rows are not
constant-latitude, so a lat/lon slice would return a skewed parallelogram.

Verified against a real file (2020-01-15 12Z): index (0,0) is 20.2923 N,
-17.4859 E, matching the documented lower-left corner, and the cropped window
spans 56.47-63.98 N, 24.20-39.65 E.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
import xarray as xr

SPEC = "domain_spec_leningrad.json"
OUT = "cerra_t2m_leningrad.zarr"


def target_window(spec_path=SPEC):
    sp = json.load(open(spec_path))
    i0, i1 = sp["target"]["i_range"]
    j0, j1 = sp["target"]["j_range"]
    nx, ny = sp["target"]["shape_xy"]
    return i0, i1, j0, j1, nx, ny


def crop_one(path, i0, i1, j0, j1, nx, ny):
    """Open one GRIB, slice the target window, return a Dataset (time, y, x)."""
    ds = xr.open_dataset(path, engine="cfgrib",
                         backend_kwargs={"indexpath": ""})
    name = list(ds.data_vars)[0]
    da = ds[name]
    full = ds.sizes.get("y"), ds.sizes.get("x")
    if full != (1069, 1069):
        raise ValueError(f"{os.path.basename(path)}: expected 1069x1069, got {full}")
    sub = da.isel(y=slice(j0, j1 + 1), x=slice(i0, i1 + 1)).astype("float32")
    if (sub.sizes["x"], sub.sizes["y"]) != (nx, ny):
        raise ValueError(f"{os.path.basename(path)}: crop is "
                         f"{sub.sizes['x']}x{sub.sizes['y']}, spec says {nx}x{ny}")
    if "time" not in sub.dims:
        sub = sub.expand_dims("time")
    out = sub.to_dataset(name="t2m")
    # keep the 2-D lat/lon so downstream station pairing needs no reprojection
    for c in ("latitude", "longitude"):
        if c in ds.coords:
            out[c] = ds[c].isel(y=slice(j0, j1 + 1), x=slice(i0, i1 + 1))
    ds.close()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src_dir", help="directory of downloaded CERRA GRIB files")
    ap.add_argument("--delete-source", action="store_true",
                    help="remove each GRIB after it is appended")
    ap.add_argument("--pattern", default="*.grib*")
    args = ap.parse_args()

    i0, i1, j0, j1, nx, ny = target_window()
    files = sorted(glob.glob(os.path.join(args.src_dir, args.pattern)))
    if not files:
        sys.exit(f"no files matching {args.pattern} in {args.src_dir}")
    print(f"{len(files)} file(s); target window {nx}x{ny} "
          f"(i {i0}..{i1}, j {j0}..{j1})", flush=True)

    n_written = 0
    for k, f in enumerate(files, 1):
        try:
            out = crop_one(f, i0, i1, j0, j1, nx, ny)
        except Exception as e:
            print(f"  [{k}/{len(files)}] SKIP {os.path.basename(f)}: {e}", flush=True)
            continue
        first = not os.path.exists(OUT)
        if first:
            out.to_zarr(OUT, mode="w")
        else:
            out.drop_vars([c for c in ("latitude", "longitude") if c in out]) \
               .to_zarr(OUT, mode="a", append_dim="time")
        n_written += out.sizes["time"]
        print(f"  [{k}/{len(files)}] {os.path.basename(f)} "
              f"+{out.sizes['time']} steps", flush=True)
        out.close()
        if args.delete_source:
            os.remove(f)

    z = xr.open_zarr(OUT)
    print(f"\n{OUT}: {dict(z.sizes)} | {n_written} steps appended this run")
    print(f"time span: {z.time.values.min()} .. {z.time.values.max()}")
    size = sum(os.path.getsize(os.path.join(r, fn))
               for r, _, fns in os.walk(OUT) for fn in fns)
    print(f"store size: {size/1e9:.2f} GB")


if __name__ == "__main__":
    main()
