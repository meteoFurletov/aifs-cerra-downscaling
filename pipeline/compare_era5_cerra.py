"""
Three-way comparison: stations (truth) vs ERA5 vs CERRA, 2020.

  python compare_era5_cerra.py era5_2020.grib

Why this matters more than a plain input/target check
-----------------------------------------------------
AIFS is TRAINED on ERA5. So ERA5's error against these stations is not just the
starting point for downscaling -- it bounds what any AIFS forecast can know
about this region's lakes and coasts before downscaling. The ERA5-minus-CERRA
gap is the headroom a downscaling model can address; the CERRA-vs-station
residual (0.875 C for 2020, measured separately) is the floor below which
improvement cannot be verified with this truth network.

Three regimes are worth separating, because they have different implications:

  * ERA5 worse than CERRA  -> real headroom; downscaling can help.
  * ERA5 == CERRA          -> no resolution signal at that site; a model can
                              only learn the identity map there.
  * ERA5 better than CERRA -> CERRA is adding error at that site. Rare, but if
                              it clusters (e.g. on lake margins) it is a
                              warning about the target, not a win for ERA5.

Pairing rule: compare ONLY at station-times where BOTH reanalyses and the
observation exist, so the two RMSEs are computed over an identical sample.
Anything else silently compares different populations.
"""
import json
import sys

import numpy as np
import pandas as pd
import pyproj
import xarray as xr

SPEC = "domain_spec_leningrad.json"
ANALYSIS_HOURS = [0, 3, 6, 9, 12, 15, 18, 21]


def load_era5_at_stations(grib_path, stations):
    """Nearest-gridpoint ERA5 2m temperature (degC) per station and time."""
    ds = xr.open_dataset(grib_path, engine="cfgrib",
                         backend_kwargs={"indexpath": ""})
    name = [v for v in ds.data_vars][0]
    da = ds[name]
    lon_name = "longitude" if "longitude" in da.dims else "lon"
    lat_name = "latitude" if "latitude" in da.dims else "lat"
    # ERA5 longitudes may be 0..360; normalise to -180..180 and sort
    lons = ((da[lon_name].values + 180) % 360) - 180
    da = da.assign_coords({lon_name: lons}).sortby(lon_name)

    sel = da.sel({lat_name: xr.DataArray(stations.lat.values, dims="station"),
                  lon_name: xr.DataArray(stations.lon.values, dims="station")},
                 method="nearest")
    # step=0 analyses: 'time' IS the valid time and cfgrib also exposes a
    # duplicate 'valid_time'. Drop the duplicate before reset_index, or the
    # merge key becomes ambiguous.
    if "valid_time" in sel.coords:
        sel = sel.drop_vars("valid_time")
    out = (sel.to_dataframe(name="t2m_era5").reset_index())
    out["sid"] = stations.sid.values[out.station.values]
    out = out[["sid", "time", "t2m_era5"]]
    if out.t2m_era5.mean() > 100:
        out["t2m_era5"] = out.t2m_era5 - 273.15
    # distance from station to the ERA5 cell centre it was matched to
    glat = sel[lat_name].values
    glon = sel[lon_name].values
    sp = json.load(open(SPEC))
    fwd = pyproj.Transformer.from_crs("EPSG:4326", sp["cerra_grid"]["proj4"],
                                      always_xy=True).transform
    d = []
    for i, r in enumerate(stations.itertuples()):
        sx, sy = fwd(r.lon, r.lat)
        gx, gy = fwd(float(glon[i]), float(glat[i]))
        d.append(np.hypot(sx - gx, sy - gy) / 1e3)
    stations = stations.assign(era5_offset_km=d)
    ds.close()
    return out, stations


def rmse(x):
    return float(np.sqrt(np.mean(np.square(x))))


def main():
    grib = sys.argv[1] if len(sys.argv) > 1 else "era5_2020.grib"
    pairs = pd.read_parquet("pairs.parquet")
    pairs["sid"] = pairs.sid.astype(str).str.zfill(11)
    idx = pd.read_csv("station_index.csv", dtype={"sid": str})
    idx["sid"] = idx.sid.str.zfill(11)

    era5, idx = load_era5_at_stations(grib, idx)
    era5["sid"] = era5.sid.astype(str).str.zfill(11)

    # inner join: identical sample for both reanalyses
    df = pairs.merge(era5, on=["sid", "time"], how="inner")
    df["resid_era5"] = df.t2m_obs - df.t2m_era5
    df["resid_cerra"] = df.resid
    df["cerra_gain"] = df.resid_era5.abs() - df.resid_cerra.abs()   # >0 = CERRA better
    df.to_parquet("three_way.parquet", index=False)

    print(f"paired sample: {len(df):,} rows | {df.sid.nunique()} stations "
          f"| {df.time.min()} .. {df.time.max()}")
    print(f"dropped vs CERRA-only pairs: {len(pairs)-len(df):,}")

    print("\n=== overall, identical sample ===")
    for lab, col in [("ERA5 (0.25 deg, AIFS training data)", "resid_era5"),
                     ("CERRA (5.5 km, downscaling target)", "resid_cerra")]:
        print(f"  {lab:38s} bias {df[col].mean():+.3f}  MAE {df[col].abs().mean():.3f} "
              f" RMSE {rmse(df[col]):.3f}")
    print(f"  headroom (ERA5 RMSE - CERRA RMSE): "
          f"{rmse(df.resid_era5) - rmse(df.resid_cerra):+.3f} C")

    print("\n=== by season ===")
    df["month"] = df.time.dt.month
    df["seas"] = np.select(
        [df.month.isin([11, 12, 1, 2]), df.month.isin([5, 6, 7, 8])],
        ["winter", "summer"], default="shoulder")
    tab = df.groupby("seas").apply(
        lambda g: pd.Series({"n": len(g), "era5": rmse(g.resid_era5),
                             "cerra": rmse(g.resid_cerra),
                             "headroom": rmse(g.resid_era5) - rmse(g.resid_cerra)}),
        include_groups=False)
    print(tab.round(3).to_string())

    print("\n=== per station: where does CERRA actually help? ===")
    st = df.groupby("sid").apply(
        lambda g: pd.Series({"n": len(g), "era5": rmse(g.resid_era5),
                             "cerra": rmse(g.resid_cerra)}),
        include_groups=False).reset_index()
    st["headroom"] = st.era5 - st.cerra
    st = st.merge(idx[["sid", "name", "country", "elev", "offset_km",
                       "era5_offset_km"]], on="sid", how="left")
    st = st[st.n > 500]
    st.to_csv("three_way_stations.csv", index=False)
    print(f"  stations where CERRA beats ERA5: {int((st.headroom > 0).sum())} of {len(st)}")
    print(f"  median headroom {st.headroom.median():+.3f} C "
          f"| range {st.headroom.min():+.3f} .. {st.headroom.max():+.3f}")
    print("\n  biggest CERRA gains:")
    print(st.nlargest(5, "headroom")[["name", "country", "era5", "cerra",
                                      "headroom", "elev"]].round(3).to_string(index=False))
    print("\n  where CERRA is WORSE than ERA5:")
    worse = st.nsmallest(5, "headroom")[["name", "country", "era5", "cerra",
                                         "headroom", "elev"]]
    print(worse.round(3).to_string(index=False))
    return df, st


if __name__ == "__main__":
    main()
