"""
Build current-era station truth from Iowa State IEM (ASOS/METAR).

  python build_station_truth_iem.py 2025-07-01 2026-05-31 station_truth_iem.parquet

Why this exists
---------------
NOAA ISD yearly files lag ~1 year: the 2025 file ends 2025-08-24 and no 2026
file exists. That limited four-way (AIFS + CERRA + ERA5 + stations) coverage to
53 summer days. IEM is current to within ~2 days, so it restores station
verification across the whole AIFS/CERRA overlap.

Three differences from ISD that MUST be respected
-------------------------------------------------
1. UNITS. IEM `tmpf` is FAHRENHEIT. ISD was tenths of a degree Celsius.

2. TIMESTAMPS. IEM serves METAR at :20 and :50 past the hour, never on the
   hour. An exact-time join returns ZERO rows (verified). Use nearest-report
   matching with a tolerance; 25 min is the natural half-window.

3. NOT INTERCHANGEABLE WITH ISD. Cross-validated on JJA 2020 over the 10 shared
   stations: median IEM-vs-ISD RMSE 0.568 C, up to 1.348 C (Petrozavodsk), with
   per-station biases to +0.33 C. That disagreement is larger than the
   ERA5-CERRA headroom (0.288 C) this project is trying to measure. The 5
   Finnish sites agree well (0.45-0.57 C, bias ~0.00); Tallinn, Tartu,
   Petrozavodsk and Pskov do not. METAR and SYNOP are different instruments and
   practices, not two views of one number.

   => Never pool IEM and ISD in one metric, and never score an IEM-based
      forecast against an ISD-derived baseline. Any stage-2 station claim
      recomputes its own CERRA/AIFS baseline from IEM alone.

Coverage: 10 of our 86 target stations match an IEM site within 3 km (ASOS is
airport-only). Power is still adequate — per-station headroom sd is 0.211 C, so
n=10 detects 0.131 C at 95%, against a true headroom of 0.288 C. The subset is
representative (median CERRA RMSE 0.768 vs 0.800 for all 86).
"""
import io
import sys
import time
import urllib.error
import urllib.request

import numpy as np
import pandas as pd
import pyproj
from scipy.spatial import cKDTree

BASE = "https://mesonet.agron.iastate.edu"
NETWORKS = ("RU__ASOS", "FI__ASOS", "EE__ASOS")
MATCH_KM = 3.0
TOL_MIN = 25
RETRIES = 4
import json

SPEC = "domain_spec_leningrad.json"


def iem_sites():
    """All stations in the three national ASOS networks."""
    rows = []
    for net in NETWORKS:
        j = json.loads(urllib.request.urlopen(
            f"{BASE}/geojson/network/{net}.geojson", timeout=120).read())
        for f in j["features"]:
            c = f["geometry"]["coordinates"]
            rows.append({"iem_id": f["id"], "iem_name": f["properties"].get("sname"),
                         "net": net, "lon": c[0], "lat": c[1]})
    return pd.DataFrame(rows)


def match_to_targets(sites):
    """Match our target-box stations to IEM sites by projected distance."""
    sp = json.load(open(SPEC))
    fwd = pyproj.Transformer.from_crs("EPSG:4326", sp["cerra_grid"]["proj4"],
                                      always_xy=True).transform
    stn = pd.read_csv("stations_expanded.csv")
    tgt = stn[stn.role == "target"].copy()
    tgt["sid"] = (tgt.USAF.astype(str).str.zfill(6)
                  + tgt.WBAN.astype(str).str.zfill(5))
    IX = np.array([fwd(r.lon, r.lat) for r in sites.itertuples()])
    TX = np.array([fwd(r.lon, r.lat) for r in tgt.itertuples()])
    d, i = cKDTree(IX).query(TX)
    tgt["iem_id"] = sites.iem_id.values[i]
    tgt["iem_name"] = sites.iem_name.values[i]
    tgt["iem_km"] = d / 1e3
    return tgt[tgt.iem_km < MATCH_KM].reset_index(drop=True)


def fetch(sid, start, end):
    """One station over the full window -> degC at 3-hourly analysis times."""
    u = (f"{BASE}/cgi-bin/request/asos.py?station={sid}&data=tmpf"
         f"&year1={start.year}&month1={start.month}&day1={start.day}"
         f"&year2={end.year}&month2={end.month}&day2={end.day}"
         f"&tz=UTC&format=onlycomma&missing=empty")
    for k in range(RETRIES):
        try:
            raw = urllib.request.urlopen(u, timeout=600).read().decode()
            break
        except Exception:
            if k == RETRIES - 1:
                return None
            time.sleep(2 ** k * 5)
    d = pd.read_csv(io.StringIO(raw))
    if "tmpf" not in d.columns or d.empty:
        return None
    d["rep"] = pd.to_datetime(d["valid"], errors="coerce")
    d["t"] = (pd.to_numeric(d["tmpf"], errors="coerce") - 32.0) * 5.0 / 9.0   # F -> C
    d = d.dropna(subset=["rep", "t"])
    d = d[d.t.abs() < 80].sort_values("rep")
    if d.empty:
        return None
    grid = pd.DataFrame({"time": pd.date_range(start, end, freq="3h")})
    out = pd.merge_asof(grid, d[["rep", "t"]], left_on="time", right_on="rep",
                        direction="nearest", tolerance=pd.Timedelta(minutes=TOL_MIN))
    out = out.dropna(subset=["t"])
    out["offset_min"] = (out.time - out.rep).dt.total_seconds().abs() / 60
    return out.rename(columns={"t": "t2m_obs"})[["time", "t2m_obs", "offset_min"]]


def main():
    start = pd.Timestamp(sys.argv[1] if len(sys.argv) > 1 else "2025-07-01")
    end = pd.Timestamp(sys.argv[2] if len(sys.argv) > 2 else "2026-05-31")
    outfile = sys.argv[3] if len(sys.argv) > 3 else "station_truth_iem.parquet"

    sites = iem_sites()
    matched = match_to_targets(sites)
    print(f"{len(sites)} IEM sites | {len(matched)} matched within {MATCH_KM} km", flush=True)

    frames = []
    for r in matched.itertuples():
        p = fetch(r.iem_id, start, end)
        if p is None or p.empty:
            print(f"  {r.iem_id} {str(r.name)[:20]:20s} EMPTY", flush=True)
            continue
        p.insert(0, "sid", r.sid)
        p["iem_id"] = r.iem_id
        p["country"] = r.country
        frames.append(p)
        print(f"  {r.iem_id} {str(r.name)[:20]:20s} {len(p):5d} rows "
              f"| median offset {p.offset_min.median():.0f} min", flush=True)

    obs = pd.concat(frames, ignore_index=True).sort_values(["sid", "time"])
    obs.to_parquet(outfile, index=False)
    exp = len(pd.date_range(start, end, freq="3h"))
    print(f"\n{outfile}: {len(obs):,} rows | {obs.sid.nunique()} stations "
          f"| {obs.time.min()} .. {obs.time.max()}")
    print(f"mean coverage: {len(obs)/obs.sid.nunique()/exp:.1%} of {exp} slots")
    print("by country:", obs.groupby("country").size().to_dict())


if __name__ == "__main__":
    main()
