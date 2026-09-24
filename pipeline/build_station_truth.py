"""
Build the station-truth table for the Leningrad+100km target box.

Source : NOAA ISD global-hourly (no credentials required).
Output : station_truth.parquet  — tidy (sid, time, t2m_obs) at CERRA analysis hours.

Two ISD details that matter and are easy to get wrong:

  * TMP is "+0056,1" — tenths of a degree plus a QC flag. Keep flags {0,1,4,5};
    the missing sentinel +9999 becomes 999.9 and is excluded by the |t|<80 test.
  * A station usually files BOTH FM-12 (SYNOP, 0.1 degC resolution) and FM-15
    (METAR, quantized to whole degrees) at the same timestamp. Averaging them
    injects ~0.63 degC RMS noise into truth (measured at Pulkovo 2020), which is
    larger than the skill differences a downscaling model is judged on. So pick
    ONE report per timestamp by priority: SYNOP first, METAR only as fallback.
"""
import io
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

YEARS = range(int(sys.argv[1]), int(sys.argv[2]) + 1) if len(sys.argv) > 2 \
    else range(2015, 2025)
OUT_PARQUET = sys.argv[3] if len(sys.argv) > 3 else "station_truth.parquet"
GOOD_QC = {"0", "1", "4", "5"}
ANALYSIS_HOURS = {0, 3, 6, 9, 12, 15, 18, 21}
RT_PRIORITY = {"FM-12": 0, "FM-13": 1, "FM-14": 2, "FM-15": 3}
BASE = "https://www.ncei.noaa.gov/data/global-hourly/access"
CACHE = "isd_cache"
MAX_WORKERS = 4          # shared public archive - stay polite
RETRIES = 3


def fetch_year(sid, year):
    """Return raw CSV bytes for one station-year, cached on disk. None if absent."""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"{sid}_{year}.csv")
    if os.path.exists(path):
        return open(path, "rb").read() or None
    url = f"{BASE}/{year}/{sid}.csv"
    for attempt in range(RETRIES):
        try:
            raw = urllib.request.urlopen(url, timeout=180).read()
            open(path, "wb").write(raw)
            return raw
        except urllib.error.HTTPError as e:
            if e.code == 404:                 # station did not report that year
                open(path, "wb").write(b"")
                return None
            time.sleep(2 ** attempt)
        except Exception:
            time.sleep(2 ** attempt)
    return None


def parse_isd_temp(raw_bytes):
    """Raw ISD CSV -> DataFrame(time, t2m_obs, REPORT_TYPE) at analysis hours."""
    d = pd.read_csv(io.BytesIO(raw_bytes), low_memory=False,
                    usecols=["DATE", "TMP", "REPORT_TYPE"])
    sp = d["TMP"].astype(str).str.split(",", n=1, expand=True)
    d["t2m_obs"] = pd.to_numeric(sp[0], errors="coerce") / 10.0
    d = d[sp[1].isin(GOOD_QC) & d.t2m_obs.notna() & (d.t2m_obs.abs() < 80)].copy()
    d["time"] = pd.to_datetime(d["DATE"], errors="coerce")
    d = d.dropna(subset=["time"])
    d = d[d.time.dt.hour.isin(ANALYSIS_HOURS) & (d.time.dt.minute == 0)]
    if d.empty:
        return d.assign(REPORT_TYPE=pd.Series(dtype=object))[["time", "t2m_obs", "REPORT_TYPE"]]
    d["prio"] = d.REPORT_TYPE.map(RT_PRIORITY).fillna(9).astype(int)
    d = d.sort_values(["time", "prio"]).drop_duplicates("time", keep="first")
    return d[["time", "t2m_obs", "REPORT_TYPE"]]


def one_station_year(sid, year):
    raw = fetch_year(sid, year)
    if not raw:
        return None
    try:
        p = parse_isd_temp(raw)
    except Exception:
        return None
    if p.empty:
        return None
    p.insert(0, "sid", sid)
    return p


def main():
    stn = pd.read_csv("stations_expanded.csv")
    tgt = stn[stn.role == "target"].copy()
    tgt["sid"] = (tgt.USAF.astype(str).str.zfill(6)
                  + tgt.WBAN.astype(str).str.zfill(5))
    jobs = [(r.sid, y) for r in tgt.itertuples() for y in YEARS]
    print(f"{len(tgt)} stations x {len(list(YEARS))} years = {len(jobs)} station-years",
          flush=True)

    frames, done, miss = [], 0, 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(one_station_year, sid, y): (sid, y) for sid, y in jobs}
        for f in as_completed(futs):
            r = f.result()
            done += 1
            if r is None:
                miss += 1
            else:
                frames.append(r)
            if done % 100 == 0:
                print(f"  {done}/{len(jobs)} fetched ({miss} empty)", flush=True)

    obs = (pd.concat(frames, ignore_index=True)
             .sort_values(["sid", "time"])
             .reset_index(drop=True))
    obs.to_parquet(OUT_PARQUET, index=False)
    print(f"\nrows={len(obs):,} stations={obs.sid.nunique()} "
          f"span={obs.time.min()} .. {obs.time.max()}", flush=True)
    print("report mix:", obs.REPORT_TYPE.value_counts().to_dict(), flush=True)
    return obs


if __name__ == "__main__":
    main()
