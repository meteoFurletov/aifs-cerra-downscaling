"""
Rebuild station verification on SYNOP truth, and assign the spatial holdout.

  python verify_on_synop.py

Inputs   station_truth_synop.parquet   (build_station_truth_synop.py)
         aifs_overlap.npz              AIFS cube
         cerra_t2m_full.zarr           CERRA target
         era5_2025H2.grib, era5_2026H1.grib
         domain_spec_leningrad.json

Outputs  synop_fourway.parquet         per (station, time, lead) with all sources
         synop_station_scores.csv      per-station bias/RMSE per source
         synop_folds.csv               spatial fold assignment
         synop_verification.png        figure

Why redo this on SYNOP
----------------------
The IEM-based verification used 10 airport stations, of which only 2 were
Russian - and IEM's METAR measurements disagree with the ISD SYNOP archive by
0.57-1.35 C, more than the effects being measured. SYNOP is the same report
type ISD carried (validated: RMSE 0.009 C against ISD on July 2020), so this
verification is directly comparable to the 2015-2024 baseline AND covers the
Russian stations that constitute the target region.

Two deliberate methodological choices, unchanged from pair_stations_cerra.py
---------------------------------------------------------------------------
* NEAREST-CELL extraction, not bilinear. CERRA and ERA5 fields are grid-box
  averages; interpolating between them invents values the dataset never claimed.
  The point-vs-box mismatch is an irreducible error floor, largest at coastlines.

* SPATIALLY CONTIGUOUS holdout folds, by k-means on projected coordinates - not
  random station assignment. Random assignment leaves held-out stations ringed
  by training stations a few km away, which is not a generalisation test. Both
  ERA5 and CERRA assimilate this station network, so a temporal split would make
  station verification circular; the split MUST be spatial.
"""
import json
import sys

import numpy as np
import pandas as pd
import pyproj
import xarray as xr
from scipy.cluster.vq import kmeans2
from scipy.interpolate import RegularGridInterpolator

N_FOLDS = 5
MAIN_HOURS = (0, 6, 12, 18)


def load_spec():
    SP = json.load(open("domain_spec_leningrad.json"))
    G, T, C = SP["cerra_grid"], SP["target"], SP["input_crop"]
    fwd = pyproj.Transformer.from_crs("EPSG:4326", G["proj4"], always_xy=True).transform
    inv = pyproj.Transformer.from_crs(G["proj4"], "EPSG:4326", always_xy=True).transform
    ll = fwd(G["origin_LL_latlon"][1], G["origin_LL_latlon"][0])
    xg = ll[0] + np.arange(G["nx"]) * G["dx_m"]
    yg = ll[1] + np.arange(G["ny"]) * G["dx_m"]
    return SP, G, T, C, fwd, inv, xg, yg


def main():
    SP, G, T, C, fwd, inv, xg, yg = load_spec()
    I0, I1 = T["i_range"]
    J0, J1 = T["j_range"]

    obs = pd.read_parquet("station_truth_synop.parquet")
    obs = obs[obs.role == "target"].copy()
    obs["sid"] = obs.sid.astype(str).str.zfill(11)
    sm = (obs.groupby("sid")
             .agg(name=("name", "first"), country=("country", "first"),
                  lat=("lat", "first"), lon=("lon", "first"), elev=("elev", "first"))
             .reset_index())
    print(f"SYNOP target-box truth: {len(obs):,} obs, {len(sm)} stations", flush=True)
    print(f"  by country: {sm.country.value_counts().to_dict()}", flush=True)

    # ---- nearest CERRA cell per station -------------------------------------
    sxy = np.array([fwd(r.lon, r.lat) for r in sm.itertuples()])
    cj = np.array([np.abs(yg[J0:J1 + 1] - p[1]).argmin() for p in sxy])
    ci = np.array([np.abs(xg[I0:I1 + 1] - p[0]).argmin() for p in sxy])
    off_km = np.array([np.hypot(xg[I0 + ci[k]] - sxy[k][0],
                                yg[J0 + cj[k]] - sxy[k][1]) / 1e3
                       for k in range(len(sm))])
    sm["cerra_offset_km"] = off_km
    print(f"  nearest-cell offset: median {np.median(off_km):.2f} km, "
          f"max {off_km.max():.2f} km", flush=True)

    c = xr.open_zarr("cerra_t2m_full.zarr")
    vc = list(c.data_vars)[0]
    carr = c[vc].values
    ct = pd.DatetimeIndex(c.time.values)
    dfc = pd.DataFrame({
        "time": np.repeat(ct, len(sm)),
        "sid": np.tile(sm.sid.values, len(ct)),
        "t2m_cerra": carr[:, cj, ci].ravel()})

    # ---- ERA5 at stations ---------------------------------------------------
    e5 = xr.concat([xr.open_dataset(f, engine="cfgrib",
                                    backend_kwargs={"indexpath": ""})
                    for f in ("era5_2025H2.grib", "era5_2026H1.grib")],
                   dim="time").sortby("time")
    v5 = list(e5.data_vars)[0]
    e5s = (e5[v5].sel(latitude=xr.DataArray(sm.lat.values, dims="station"),
                      longitude=xr.DataArray(sm.lon.values, dims="station"),
                      method="nearest") - 273.15)
    if "valid_time" in e5s.coords:            # cfgrib duplicates the time coord
        e5s = e5s.drop_vars("valid_time")
    df5 = e5s.to_dataframe(name="t2m_era5").reset_index()
    df5["sid"] = sm.sid.values[df5.station.values]
    df5 = df5[["sid", "time", "t2m_era5"]]

    base = (obs[["sid", "time", "t2m_obs"]]
            .merge(df5, on=["sid", "time"])
            .merge(dfc, on=["sid", "time"]))
    print(f"\nstations n ERA5 n CERRA: {len(base):,} rows, "
          f"{base.sid.nunique()} stations", flush=True)

    # ---- AIFS at stations, per lead -----------------------------------------
    z = np.load("aifs_overlap.npz")
    cube = z["cube"]
    ti = pd.to_datetime(z["init_time"], unit="s")
    leads = z["lead_h"]
    lo0, la0, lo1, la1 = C["bbox_latlon"]
    glat = np.arange(90, -90.25, -0.25)
    glon = np.arange(0, 360, 0.25)
    alat = glat[(glat <= la1) & (glat >= la0)]
    alon = glon[(glon >= lo0 % 360) & (glon <= lo1 % 360)]
    assert cube.shape[-2:] == (len(alat), len(alon)), \
        f"AIFS grid mismatch: cube {cube.shape[-2:]} vs derived " \
        f"({len(alat)}, {len(alon)})"
    iy = np.array([np.abs(alat - r.lat).argmin() for r in sm.itertuples()])
    ix = np.array([np.abs(alon - (r.lon % 360)).argmin() for r in sm.itertuples()])

    frames = []
    for li, L in enumerate(leads):
        vt = ti + pd.Timedelta(hours=int(L))
        f = pd.DataFrame({
            "time": np.repeat(vt, len(sm)),
            "sid": np.tile(sm.sid.values, len(vt)),
            "t2m_aifs": cube[:, li, 1][:, iy, ix].ravel(),
            "aifs_sd": cube[:, li, 2][:, iy, ix].ravel()})
        f["lead_h"] = int(L)
        frames.append(f.merge(base, on=["sid", "time"], how="inner"))
    df = pd.concat(frames, ignore_index=True)
    for tag in ("aifs", "era5", "cerra"):
        df[f"resid_{tag}"] = df[f"t2m_{tag}"] - df.t2m_obs

    # ---- spatial folds ------------------------------------------------------
    P = np.array([fwd(r.lon, r.lat) for r in sm.itertuples()]) / 1e3
    cent, lab = kmeans2(P, N_FOLDS, minit="++", seed=0)
    sm["fold"] = lab
    df = df.merge(sm[["sid", "fold", "country", "name", "cerra_offset_km"]], on="sid")
    print("\nspatial folds (k-means on projected coords):", flush=True)
    print(sm.groupby("fold").agg(n=("sid", "size"),
                                 countries=("country", lambda s: sorted(set(s)))
                                 ).to_string(), flush=True)

    # ---- scores -------------------------------------------------------------
    rows = []
    for L, g in df.groupby("lead_h"):
        for tag in ("aifs", "era5", "cerra"):
            r_ = g[f"resid_{tag}"]
            rows.append({"lead_h": int(L), "source": tag, "n": len(g),
                         "bias": r_.mean(),
                         "rmse": float(np.sqrt((r_ ** 2).mean()))})
    sc = pd.DataFrame(rows)
    piv = sc.pivot(index="lead_h", columns="source", values="rmse")[
        ["aifs", "era5", "cerra"]]
    print("\nRMSE vs SYNOP truth (identical samples per row):", flush=True)
    print(piv.round(3).to_string(), flush=True)

    st = (df[df.lead_h == 24].groupby(["sid", "name", "country", "fold"])
          .apply(lambda g: pd.Series({
              "n": len(g),
              "era5": float(np.sqrt((g.resid_era5 ** 2).mean())),
              "cerra": float(np.sqrt((g.resid_cerra ** 2).mean())),
              "aifs24": float(np.sqrt((g.resid_aifs ** 2).mean())),
              "cerra_bias": g.resid_cerra.mean()}), include_groups=False)
          .reset_index())
    st["headroom"] = st.era5 - st.cerra
    print(f"\nper-station headroom (ERA5 - CERRA): mean {st.headroom.mean():+.3f} "
          f"sd {st.headroom.std():.3f} | positive at "
          f"{(st.headroom > 0).mean():.0%} of stations", flush=True)

    df.to_parquet("synop_fourway.parquet", index=False)
    st.round(4).to_csv("synop_station_scores.csv", index=False)
    sm.round(4).to_csv("synop_folds.csv", index=False)
    sc.round(4).to_csv("synop_summary.csv", index=False)
    print("\nwrote synop_fourway.parquet, synop_station_scores.csv, "
          "synop_folds.csv, synop_summary.csv", flush=True)
    return df, st, sm, sc


if __name__ == "__main__":
    main()
