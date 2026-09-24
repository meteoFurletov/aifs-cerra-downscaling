"""
Build station truth for 2025-2026 from raw WMO SYNOP bulletins (OGIMET).

  python build_station_truth_synop.py [start YYYY-MM] [end YYYY-MM] [out.parquet]

Why this instead of IEM
-----------------------
IEM's ASOS networks are airport-only and reach just 10 of our 86 target-box
stations - and only 2 of the 41 RUSSIAN ones, which are the target region. Worse,
IEM serves METAR, which disagrees with the ISD SYNOP archive by 0.57-1.35 C, more
than the effect this project measures.

OGIMET serves the SYNOP bulletins themselves - the SAME reports ISD archived.
Validated against ISD on July 2020: bias +0.001 C, RMSE 0.009 C at Babaevo and
0.000 C at Belogorka. That is byte-identical decoding, not a correlated proxy.
So SYNOP truth for 2025-26 IS comparable to the 2015-2024 ISD truth, which
removes the cross-source incomparability that limited stage-2 verification.

Decoding the 1sTTT group correctly
----------------------------------
FM-12 layout:  AAXX YYGGi_w  IIiii  iihVV  Nddff  [00fff]  1sTTT  2sTTT  ...

A regex for `1\\d{4}` is WRONG: the iihVV group (token 3) also starts with 1
(e.g. `11460` = visibility/cloud), and matching it yields absurd values like
-46.0 C between readings of +2 C. This was hit in-session.

Correct rule: scan tokens from index 5 onward (past AAXX, date, station id,
iihVV, Nddff), take the first 5-char token starting `1` whose second character
is 0 or 1 (the sign), and stop at any `2`-group (dewpoint) - if we reach that,
no temperature was reported. Section 3 (after ` 333`) repeats groups with
different meanings and must be discarded first.

Fetch by WMO BLOCK, not by station
----------------------------------
The `block=` parameter accepts a 2-digit WMO block, returning EVERY station in
it - measured: block 26 gives 139 distinct stations in one request. Our 86
target stations span only 4 blocks (02 Finland, 22/26/27 Russia, 26 Estonia),
so the whole 11-month pull is 4 x 11 = 44 requests instead of 86 x 11 = 946.
A 22x reduction, ~20 min instead of ~7 h.

It is also strictly better data: block requests return all stations in the
block, so the 224 input-crop stations inside these blocks arrive at no extra
cost. Those are unusable as target-box truth but valuable for checking whether
the model's boundary behaviour is sane.

Rate limits
-----------
OGIMET returns `HTTP 501 ... quota limit for slow queries` if hit too fast.
One block-month per request with a ~25 s delay works. The spool makes the run
resumable, so an interruption costs only the request in flight.

Reporting cadence (not a defect)
--------------------------------
Russian stations report the MAIN synoptic hours (00/06/12/18) near-completely
but the intermediate hours (03/09/15/21) only ~1/3 as often, so per-station
coverage of the 3-hourly grid looks like ~50%. This costs nothing here: AIFS
inits are at 00/12 and all leads used are multiples of 24 h, so every
forecast-target valid time is 00 or 12 - both main synoptic hours.
"""
import os
import re
import sys
import time
import urllib.error
import urllib.request

import numpy as np
import pandas as pd

SPOOL = "synop_spool"
DELAY_S = 25
BACKOFF_S = 180
ANALYSIS_HOURS = {0, 3, 6, 9, 12, 15, 18, 21}


def decode_temp(report):
    """FM-12 section-1 group 1sTTT -> degC, or NaN.

    See the module docstring: position-based, not regex-based, because the
    iihVV group also starts with '1'.
    """
    body = report.split(" 333")[0].replace("=", "")
    toks = body.split()
    if len(toks) < 6 or toks[0] != "AAXX":
        return np.nan
    for tk in toks[5:]:
        if len(tk) != 5:
            continue
        if tk[0] == "2":                      # dewpoint group: temp absent
            break
        if tk[0] == "1" and tk[1] in "01" and tk[2:].isdigit():
            ttt = int(tk[2:])
            return np.nan if ttt == 999 else (-1 if tk[1] == "1" else 1) * ttt / 10.0
    return np.nan


LINE_CAP = 200000        # OGIMET truncates the response at exactly this many lines


def fetch_window(block, y, m, d0, d1, tries=4):
    """One block-window of decoded SYNOP temperatures, all stations in the block.

    RESPONSE CAP: OGIMET truncates at exactly 200,000 lines, and the response is
    sorted STATION-major, so a truncated reply silently loses the high-numbered
    stations entirely rather than losing the tail of the period. A full block-month
    for block 02 (366 stations) hits the cap. Windows of <= 10 days stay well under
    it; the caller asserts on the cap so truncation can never pass unnoticed.
    """
    url = (f"https://www.ogimet.com/cgi-bin/getsynop?block={block}"
           f"&begin={y}{m:02d}{d0:02d}0000"
           f"&end={y}{m:02d}{d1:02d}2100")
    for k in range(tries):
        try:
            raw = urllib.request.urlopen(url, timeout=300).read().decode("utf-8", "replace")
            break
        except urllib.error.HTTPError as e:
            if e.code == 501 and k < tries - 1:      # quota
                time.sleep(BACKOFF_S)
                continue
            return None
        except Exception:
            if k == tries - 1:
                return None
            time.sleep(30)
    lines = raw.strip().splitlines()
    if len(lines) >= LINE_CAP:
        raise RuntimeError(
            f"block {block} {y}-{m:02d} d{d0}-{d1}: hit the {LINE_CAP}-line cap "
            f"({len(lines)} lines) - response is station-major so high-numbered "
            f"stations are silently missing. Use a shorter window.")
    rows = []
    for line in lines:
        p = line.split(",", 6)
        if len(p) < 7:
            continue
        t = decode_temp(p[6])
        if np.isnan(t):
            continue
        ts = pd.Timestamp(f"{p[1]}-{p[2]}-{p[3]} {p[4]}:{p[5]}")
        if ts.hour in ANALYSIS_HOURS and ts.minute == 0:
            rows.append({"wmo": p[0].strip(), "time": ts, "t2m_obs": t})
    d = pd.DataFrame(rows)
    if not len(d):
        return d
    return d.drop_duplicates(["wmo", "time"]).sort_values(["wmo", "time"])


def main():
    start = pd.Period(sys.argv[1] if len(sys.argv) > 1 else "2025-07")
    end = pd.Period(sys.argv[2] if len(sys.argv) > 2 else "2026-05")
    outfile = sys.argv[3] if len(sys.argv) > 3 else "station_truth_synop.parquet"

    stn = pd.read_csv("stations_expanded.csv")
    stn["sid"] = (stn.USAF.astype(str).str.zfill(6)
                  + stn.WBAN.astype(str).str.zfill(5)).str.zfill(11)
    stn["wmo"] = stn.USAF.astype(str).str.zfill(6).str[:5]
    tg = stn[stn.role == "target"]
    blocks = sorted(tg.wmo.str[:2].unique())
    months = pd.period_range(start, end, freq="M")
    # 10-day windows keep every response under the 200k-line truncation cap
    windows = []
    for m in months:
        nd = m.days_in_month
        for d0, d1 in ((1, 10), (11, 20), (21, nd)):
            windows.append((m.year, m.month, d0, d1))
    os.makedirs(SPOOL, exist_ok=True)
    total = len(blocks) * len(windows)
    print(f"{len(blocks)} blocks {blocks} x {len(windows)} windows = {total} requests "
          f"(covers all {len(tg)} target stations)", flush=True)

    done = 0
    t0 = time.time()
    for blk in blocks:
        for (y, mo, d0, d1) in windows:
            path = os.path.join(SPOOL, f"blk{blk}_{y}{mo:02d}_{d0:02d}.parquet")
            done += 1
            if os.path.exists(path):
                continue
            try:
                d = fetch_window(blk, y, mo, d0, d1)
            except RuntimeError as e:                 # truncation - never silent
                print(f"  TRUNCATION {e}", flush=True)
                continue
            if d is None:
                print(f"  block {blk} {y}-{mo:02d} d{d0} FAILED", flush=True)
                continue
            d.to_parquet(path, index=False)
            el = time.time() - t0
            print(f"  {done}/{total} blk {blk} {y}-{mo:02d} d{d0:02d}-{d1:02d}: "
                  f"{len(d):6d} rows, {d.wmo.nunique() if len(d) else 0:3d} stns | "
                  f"eta {(total-done)*el/max(done,1)/60:.0f} min", flush=True)
            time.sleep(DELAY_S)

    parts = [pd.read_parquet(os.path.join(SPOOL, f))
             for f in sorted(os.listdir(SPOOL))
             if f.startswith("blk") and f.endswith(".parquet")]
    raw = pd.concat([p for p in parts if len(p)], ignore_index=True)
    # keep only stations in our inventory; attach sid/country/role
    meta = stn[["wmo", "sid", "name", "country", "role", "lat", "lon", "elev"]]
    obs = raw.merge(meta, on="wmo", how="inner")
    obs = obs.drop_duplicates(["sid", "time"]).sort_values(["sid", "time"])
    obs.to_parquet(outfile, index=False)

    exp_main = len(pd.date_range(start.start_time, end.end_time, freq="6h"))
    tgt = obs[obs.role == "target"]
    print(f"\n{outfile}: {len(obs):,} obs | {obs.sid.nunique()} stations "
          f"| {obs.time.min()} .. {obs.time.max()}", flush=True)
    print(f"  target-box : {len(tgt):,} obs, {tgt.sid.nunique()} stations", flush=True)
    print(f"  by country : {tgt.groupby('country').sid.nunique().to_dict()}", flush=True)
    main_h = tgt[tgt.time.dt.hour.isin([0, 6, 12, 18])]
    print(f"  main-hour coverage (00/06/12/18): "
          f"{len(main_h)/max(tgt.sid.nunique(),1)/exp_main:.1%}", flush=True)
    print(f"  input-crop stations also captured: "
          f"{obs[obs.role != 'target'].sid.nunique()}", flush=True)


if __name__ == "__main__":
    main()
