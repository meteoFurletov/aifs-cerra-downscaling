"""
Stage-1 CERRA retrieval for the Leningrad+100km target box.

CDS has NO area-subsetting for CERRA: each request returns the full 1069x1069
Lambert field. This script therefore downloads month-by-month, crops to the
target index window immediately, appends to a zarr store, and DELETES the GRIB.
Peak disk stays ~ one month of GRIB (~0.6 GB) instead of the full 280 GB.

Requires a CDS personal access token in ~/.cdsapirc  (see cds.climate.copernicus.eu).
"""
import os, json, numpy as np, xarray as xr, cdsapi

SPEC   = json.load(open("domain_spec_leningrad.json"))
I0, I1 = SPEC["target"]["i_range"]
J0, J1 = SPEC["target"]["j_range"]
YEARS  = [str(y) for y in range(2015, 2025)]      # 10-yr pretrain span
MONTHS = [f"{m:02d}" for m in range(1, 13)]
TIMES  = ["00:00","03:00","06:00","09:00","12:00","15:00","18:00","21:00"]
OUT    = "cerra_t2m_leningrad.zarr"

c = cdsapi.Client()
for y in YEARS:
    for m in MONTHS:
        tmp = f"_cerra_{y}{m}.grib"
        if not os.path.exists(tmp):
            c.retrieve("reanalysis-cerra-single-levels", {
                "variable": ["2m_temperature"],
                "level_type": "surface_or_atmosphere",
                "data_type": ["reanalysis"],
                "product_type": "analysis",
                "year": [y], "month": [m],
                "day": [f"{d:02d}" for d in range(1, 32)],
                "time": TIMES,
                "data_format": "grib",
            }, tmp)
        ds = xr.open_dataset(tmp, engine="cfgrib")
        var = [v for v in ds.data_vars][0]
        # CERRA is on a projected 1069x1069 grid -> crop by index, not by lat/lon
        sub = ds[var].isel(y=slice(J0, J1 + 1), x=slice(I0, I1 + 1)).astype("float32")
        sub.to_dataset(name="t2m").to_zarr(OUT, mode="a", append_dim="time")
        ds.close()
        os.remove(tmp)                      # <- keeps peak disk bounded
        print(f"{y}-{m} appended, GRIB discarded", flush=True)
