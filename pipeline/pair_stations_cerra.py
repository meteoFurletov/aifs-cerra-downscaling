"""
Pair station observations to CERRA grid cells, and assign the spatial holdout.

  python pair_stations_cerra.py

Inputs   station_truth.parquet          (build_station_truth.py)
         cerra_t2m_leningrad.zarr       (crop_cerra_grib.py)
         stations_expanded.csv, domain_spec_leningrad.json
Output   pairs.parquet                  (sid, time, t2m_obs, t2m_cerra, fold, ...)
         station_index.csv              per-station cell index, offset, fold

Design notes
------------
* NEAREST CELL, not bilinear. CERRA fields are grid-box averages (2.5-5.5 km
  scale), so interpolating between boxes invents a value that the reanalysis
  never claimed. The station-vs-box mismatch is a genuine error floor, largest
  near coasts and lake margins; record the offset distance so it can be used as
  a covariate or a filter rather than being silently smoothed away.

* SPATIAL holdout, not temporal. Both ERA5 and CERRA assimilate this station
  network, so a train/test split in TIME leaks: the model would be scored
  against observations the target reanalysis already saw. Splitting in SPACE
  (whole stations held out) keeps the held-out sites out of training entirely.
  Folds are built by KMeans on projected coordinates so each fold is a
  contiguous block -- random station assignment would leave held-out sites
  ringed by training sites a few km away, which is not a real generalisation
  test.
"""
import json

import numpy as np
import pandas as pd
import pyproj
import xarray as xr
from sklearn.cluster import KMeans

SPEC = "domain_spec_leningrad.json"
N_FOLDS = 5
SEED = 0


def main():
    sp = json.load(open(SPEC))
    proj = sp["cerra_grid"]["proj4"]
    fwd = pyproj.Transformer.from_crs("EPSG:4326", proj, always_xy=True).transform

    obs = pd.read_parquet("station_truth.parquet")
    z = xr.open_zarr("cerra_t2m_leningrad.zarr")
    lat = z["latitude"].values
    lon = ((z["longitude"].values + 180) % 360) - 180

    stn = pd.read_csv("stations_expanded.csv")
    stn = stn[stn.role == "target"].copy()
    stn["sid"] = (stn.USAF.astype(str).str.zfill(6)
                  + stn.WBAN.astype(str).str.zfill(5))
    stn = stn[stn.sid.isin(obs.sid.unique())].reset_index(drop=True)

    # nearest cell in PROJECTED space (lat/lon distance is anisotropic here)
    gx, gy = fwd(lon.ravel(), lat.ravel())
    gx = np.asarray(gx).reshape(lat.shape)
    gy = np.asarray(gy).reshape(lat.shape)
    rows = []
    for r in stn.itertuples():
        sx, sy = fwd(r.lon, r.lat)
        d = np.hypot(gx - sx, gy - sy)
        jy, ix = np.unravel_index(np.argmin(d), d.shape)
        rows.append({"sid": r.sid, "name": r.name, "country": r.country,
                     "lat": r.lat, "lon": r.lon, "elev": r.elev,
                     "y_idx": int(jy), "x_idx": int(ix),
                     "cell_lat": float(lat[jy, ix]), "cell_lon": float(lon[jy, ix]),
                     "offset_km": float(d[jy, ix] / 1e3),
                     "px": float(sx), "py": float(sy)})
    idx = pd.DataFrame(rows)

    # contiguous spatial folds
    km = KMeans(n_clusters=N_FOLDS, random_state=SEED, n_init=10)
    idx["fold"] = km.fit_predict(idx[["px", "py"]].values)

    # extract the CERRA value at each station cell, for every analysis time
    t2m = z["t2m"]
    sel = t2m.isel(y=xr.DataArray(idx.y_idx.values, dims="station"),
                   x=xr.DataArray(idx.x_idx.values, dims="station"))
    cer = (sel.to_dataframe(name="t2m_cerra").reset_index()
              .assign(sid=lambda d: idx.sid.values[d.station])
              [["sid", "time", "t2m_cerra"]])
    if cer.t2m_cerra.mean() > 100:                     # Kelvin -> degC
        cer["t2m_cerra"] = cer.t2m_cerra - 273.15

    pairs = (obs.merge(cer, on=["sid", "time"], how="inner")
                .merge(idx[["sid", "name", "country", "fold", "offset_km", "elev"]],
                       on="sid", how="left"))
    pairs["resid"] = pairs.t2m_obs - pairs.t2m_cerra

    pairs.to_parquet("pairs.parquet", index=False)
    idx.drop(columns=["px", "py"]).to_csv("station_index.csv", index=False)

    print(f"pairs: {len(pairs):,} rows | stations {pairs.sid.nunique()} "
          f"| span {pairs.time.min()} .. {pairs.time.max()}")
    print(f"nearest-cell offset (km): median {idx.offset_km.median():.2f} "
          f"max {idx.offset_km.max():.2f}")
    print("\nfold sizes (stations):", idx.fold.value_counts().sort_index().to_dict())
    print("\nCERRA-vs-station residual, degC:")
    print(f"  bias {pairs.resid.mean():+.3f}  MAE {pairs.resid.abs().mean():.3f} "
          f"  RMSE {np.sqrt((pairs.resid**2).mean()):.3f}")
    print("\nby country:")
    print(pairs.groupby("country")["resid"]
               .agg(n="size", bias="mean",
                    rmse=lambda x: float(np.sqrt((x**2).mean()))).round(3).to_string())
    return pairs, idx


if __name__ == "__main__":
    main()
