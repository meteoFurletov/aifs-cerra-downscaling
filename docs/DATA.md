# Data for AIFS downscaling over Leningrad Oblast

**Task.** Downscale ECMWF AIFS ENS 2 m temperature forecasts (0.25°, ~28 × 14 km at
60 °N) to the CERRA regional reanalysis grid (5.5 km) over Leningrad Oblast and its
surroundings, then verify against surface stations.

**Two stages.** Stage 1 pretrains on analysis→analysis pairs (ERA5 → CERRA), which
contain no forecast error. Stage 2 fine-tunes on forecast→analysis pairs
(AIFS → CERRA), which do. The order matters: a model trained only on stage-1 pairs
never sees forecast error and will sharpen a wrong forecast confidently.

Every number below was measured in-session, not taken from documentation. Machine-readable
form: `domain_spec_leningrad.json`.

---

## 1. Geometry

### CERRA native grid

| | |
|---|---|
| Projection | Lambert conformal conic, `+proj=lcc +lat_0=50 +lon_0=8 +lat_1=50 +lat_2=50 +R=6371229` |
| Size | 1069 × 1069 |
| Spacing | 5500 m |
| SW corner (cell 0,0) | 20.2923 °N, −17.4859 °E |

Verified against a real GRIB file: the corner-derived span matches (1069 − 1) × 5.5 km
to the metre, and the file's own index (0,0) is the corner above.

### Target window — what the model predicts

| | |
|---|---|
| Shape | 127 × 123 = 15,621 cells |
| Native index range | i 707–833, j 720–842 |
| Corners (lat, lon) | SW 58.24, 24.20 · SE 56.47, 35.19 · NE 61.96, 39.65 · NW 63.98, 27.06 |

Snapped to native grid indices so no interpolation is needed on the target side.

The box is **Leningrad Oblast + 100 km, extended north** until Ladoga, Onega and Saimaa
are each fully contained. A plain +100 km buffer left Onega only 82 % covered; whole
lakes cost 10 % more cells and are worth it, since lake–land contrast is the main
sub-grid signal here.

### Input crop — what the model sees

| | |
|---|---|
| Shape | 237 × 233 CERRA cells (= target + 300 km on every side) |
| Bounding box | 18.43 – 47.38 °E, 52.94 – 67.10 °N |
| AIFS/ERA5 grid | 0.25°, 57 × 116 (AIFS) / 59 × 118 (ERA5) |

**The 300 km margin is not padding.** At 15 m/s, air crosses 324 km in 6 h. A model
predicting the target box from an input crop of the same size cannot know what is
advecting in. Cropping the target is free; cropping the input breaks the physics.

> **Trap.** The AIFS crop is 57 × 116 and the ERA5 crop is 59 × 118 — different slicing
> conventions on the same 0.25° grid. Never index one with the other's coordinates.
> Derive each from its own source. An assertion caught this in-session; without it the
> station extraction would have been silently offset.

---

## 2. Sources

### AIFS ENS — model input

51-member AI ensemble, from the dynamical.org Zarr archive.

| | |
|---|---|
| Inits | 1,678 total, 2025-07-02 → 2026-08-25, **zero missing** |
| Cycles | 00/06/12/18 UTC, exactly 6-hourly |
| Leads | 61 steps, 0–360 h, 6-hourly |

**Units gotcha.** This store serves `temperature_2m` in **degree_Celsius**, not Kelvin
(`units: 'degree_Celsius'`). ERA5 from the ARCO archive *is* Kelvin. Applying −273.15 to
AIFS produces −271 °C means, which is how the error was caught.

**Chunking decides the access pattern.** Chunks are `(1, 61, 51, 32, 32)` — one chunk
holds *all* leads and *all* members for a 32 × 32 tile. Measured:

| Request | Time |
|---|---|
| 1 init, 1 lead, 51 members | 24.4 s |
| 1 init, 1 lead, **1 member** | 37.4 s |
| 1 init, **5 leads**, 1 member | 39.8 s |
| 8 inits, 1 lead, 1 member | 62.3 s |

Subsetting members or leads saves nothing; cost scales with **inits only**. So read each
init once, keep every lead wanted, and reduce the member axis immediately. Raw 51-member
storage for the overlap would be ~1.1 TB; the (control, mean, sd) reduction is 209 MB.

**`lead_time = 0` exists and is real** — but it is 51 *perturbed* analyses, not one state.
Spread is already 0.53 °C at lead 0, growing to 2.75 °C at +168 h, so a large fraction of
short-range spread is initial-condition uncertainty rather than model error growth.

**`ensemble_member = 0` is the unperturbed control.** Verified on ensemble geometry alone
(independent of any analysis): closest to the ensemble centroid in **16 of 16** inits
tested across all four cycles, mean distance 0.047 °C against 0.580 °C for members 1–50 —
12.5× closer. Use it when a single best-estimate field is wanted; use `ens_mean` as model
input (§5).

### CERRA — downscaling target

| | |
|---|---|
| Coverage | 1984-09 → **2026-05-31** (verified by probing, not from metadata) |
| Cadence | 3-hourly analyses, 00/03/…/21 UTC |
| Resolution | 5.5 km |

End date established by data, not documentation: 2025-07, 2025-10, 2026-01, 2026-05 and
2026-05-31 all return successful assets; 2026-06 and 2026-07 are rejected `400 invalid
combination`.

> **No area subsetting.** Unlike ERA5, `reanalysis-cerra-single-levels` accepts no `area`
> parameter. Every request returns the full 1069 × 1069 field at 2.29 MB, and the target
> is 1.4 % of it. A year is 6.7 GB downloaded for 0.17 GB kept.

**Queue behaviour, and a correction.** A single-field 2020 request returned in 0.4 s and a
full 2020 year in 21 s, which suggested "queue time is flat, request by year." That
generalised badly: the 2025–26 multi-month requests took >25 min to start. The mechanism
is a **per-user concurrency limit of 1** on the MARS archive (observed: `Running 0 —
Queued 2` for our own jobs, against `Running 65 — Queued 928` on the shared C3S archive).
Requests serialise regardless of size, so the operational rule is *maximise work per
request* — and never submit probe requests while a real job is pending, since each one
takes the single slot.

### ERA5 — stage-1 input, and AIFS's training data

| | |
|---|---|
| Coverage | 1940 → 2026-08-19 |
| Resolution | 0.25°, hourly (we request the 8 CERRA analysis times) |

ERA5 matters twice over: it is the stage-1 input *and* what AIFS was trained on, so its
station error bounds what an AIFS forecast can know about this region before downscaling.

**It accepts `area`.** One year over the input crop is 41 MB against CERRA's 6.7 GB — a
163× difference, entirely from server-side cropping (measured 14.0 kB per field for
6,962 cells, matching simple GRIB packing arithmetic). Note ERA5 was *slower* in the
queue (142 s vs 21 s for the same field count); the win is bytes, not latency.

> If ERA5 retrieval has ever felt slow: check you are using
> `reanalysis-era5-single-levels` (CDS disk) and not `reanalysis-era5-complete` (MARS
> tape, hours to days), always pass `area`, and request only the timesteps needed.

### Stations — truth

Three sources. **SYNOP is primary for 2025–26**; ISD covers 2015–24; IEM is a cross-check
only, and is **not interchangeable** with the other two (see §4).

| | ISD | **SYNOP (OGIMET)** | IEM |
|---|---|---|---|
| Product | NOAA Integrated Surface Database | **raw WMO FM-12 bulletins** | Iowa State ASOS/METAR |
| Report type | SYNOP (+ METAR fallback) | **SYNOP** | METAR |
| Period held | 2015-01 → 2024-12 | **2025-07 → 2026-05** | 2025-07 → 2026-05 |
| Sites in target box | 86 (41 RU, 33 FI, 12 EE) | **85 (41 RU, 32 FI, 12 EE)** | 10 (2 RU) |
| Observations | 2,185,758 | **202,089** (target box) | 26,678 |
| Coverage | 97–99.6 % median | **91.1 %** of main hours | 99.8 % |

The station list was originally Russia-only by construction — every WMO block was
Russian (22/23/26/27/37). Adding Finnish and Estonian sites doubled the target-box set
from 41 to 86 and cut median nearest-neighbour spacing from 56.6 km to 43.5 km, so the
network genuinely densified rather than merely extending westward.

**Why SYNOP rather than IEM for 2025–26.** ISD's yearly files lag about a year (the 2025
file ends 2025-08-24; no 2026 file exists). IEM is current but its ASOS networks are
airport-only — 10 of 86 stations, and only **2 of the 41 Russian ones** that constitute
the target region. OGIMET serves the SYNOP bulletins themselves, the same reports ISD
archived: validated against our own ISD truth on July 2020, **bias +0.001 °C and RMSE
0.009 °C** at Babaevo, 0.000 at Belogorka. That is identical decoding, so 2025–26 SYNOP
truth is directly comparable to the 2015–24 ISD baseline — which removes the
cross-source incomparability that had forced two separate verification tracks.

**Retrieval.** Fetch by 2-digit **WMO block**, not by station: one request returns every
station in the block (block 02 → 356 stations). Our 86 target stations span 4 blocks, so
the 11-month pull is 132 requests instead of 946 — and 214 input-crop stations arrive
free. Rate limit is one query per IP per 20 s, so nothing else may touch the host during
a run.

**Coverage of 91.1 % is of main synoptic hours, not of all 3-hourly slots.** Russian
stations report 00/06/12/18 near-completely but 03/09/15/21 only about a third as often.
This costs nothing here: AIFS inits are 00/12 and all leads are multiples of 24 h, so
every forecast-target valid time is 00 or 12.

---

## 3. Derived datasets

| File | Contents |
|---|---|
| `aifs_overlap.npz` | `cube` (667, 6, 3, 57, 116) float32 — (init, lead, field, lat, lon); `field` = control, ens_mean, ens_sd. 209 MB |
| `cerra_t2m_full.zarr` | 2,680 analyses on 123 × 127, 2025-07-01 → 2026-05-31. 0 duplicates, 0 missing 3-h slots, 0 NaNs. 87 MB |
| `stage2_pairs.npz` | `X` (3240, 3, 57, 116), `Y` (3240, 123, 127), plus `lead_h`, `init`, `valid`, `fold`. 269 MB |
| `cerra_static_target.npz` | `orog` (−2.9 to 301.4 m) and `lsm` (water = 16.3 % of box) on the target grid |
| `station_truth_iem.parquet` | 2025–26 truth: `sid, time, t2m_obs, offset_min, iem_id, country` |
| `station_truth.parquet` | 2015–24 truth: `sid, time, t2m_obs, REPORT_TYPE` |
| `fourway_stations.parquet` | 26,678 rows with stations + ERA5 + CERRA at identical times |
| `cerra_t2m_leningrad.zarr` | CERRA 2020 (2,928 analyses) — stage-1 target |
| `era5_2020.grib` / `era5_2025H2.grib` / `era5_2026H1.grib` | ERA5 over the input crop |

### Fold design

13 contiguous **21-day blocks** with a **5-day gap** discarded at each boundary
(18.4 % of samples), 252 samples per fold. Random splitting would be wrong: inits are
12 h apart and forecasts from adjacent inits overlap heavily in valid time.

The gap was measured, and the measurement needed two corrections. Raw autocorrelation of
the +24 h domain-mean field is r = 0.82 at 21 days — but that is the **seasonal cycle**
(seasonal sd 9.27 °C vs weather-anomaly sd 3.60 °C), not predictability. Deseasonalising
then gave a spurious r = −0.149 at half-day lag, because 00Z/12Z alternation aliases the
diurnal cycle. Working within a single init cycle gives the real decay:

| lag | 1 d | 2 d | 3 d | 5 d | 7 d | 10 d | 14 d |
|---|---|---|---|---|---|---|---|
| 00Z | 0.87 | 0.65 | 0.48 | **0.32** | 0.22 | 0.12 | −0.09 |
| 12Z | 0.90 | 0.71 | 0.55 | **0.34** | 0.18 | 0.06 | −0.09 |

5 days puts adjacent folds at r ≈ 0.33 for 18.4 % sample cost; 7 days costs 25 % to reach
r = 0.20. At n ≈ 3,000 that trade is not worth it.

> **This is a temporal split, correct only for stage 2**, whose loss is against gridded
> CERRA. Station verification needs a **spatial** holdout, because both ERA5 and CERRA
> assimilate the station network and a temporal split would make station scores circular.

---

## 4. Traps

Each of these was hit in-session and would have silently corrupted results.

**1. SYNOP vs METAR at the same timestamp (ISD).** Stations file two report types at the
same time: FM-12 (SYNOP) at 0.1 °C resolution, and FM-15 (METAR) quantised to whole
degrees. At one probe station 99.8 % of analysis-hour timestamps had both. Averaging them
— the natural thing to do with apparent duplicates — injects **0.63 °C RMS** of rounding
noise, larger than the skill differences being measured, and would appear as an
unexplained noise floor the model could never train past. Select one report per timestamp
by type priority; `build_station_truth.py` does this.

**2. ISD and IEM are not the same measurement.** Cross-validated on JJA 2020 at the 10
shared stations: median disagreement 0.568 °C, up to **1.348 °C**, with biases to
+0.33 °C. That exceeds the ERA5→CERRA headroom the project is trying to detect. The five
Finnish sites agree well (0.45–0.57 °C); Tallinn, Tartu, Petrozavodsk and Pskov do not —
visible in the data itself, since Russian sites report *on* the hour (SYNOP) while Nordic
ones report at :10 (METAR).
**Never pool the two in one metric, and never score an IEM-based result against an
ISD-derived baseline.**

**3. IEM timestamps never land on the hour.** METAR reports arrive at :20 and :50, so an
exact-time join returns **zero rows**. Use nearest-report matching (25 min tolerance).
Also: IEM `tmpf` is **Fahrenheit**.

**4. Station IDs must stay strings.** Writing the station index to CSV round-trips `sid`
as an integer and strips the leading zeros Finnish and Estonian identifiers need, silently
breaking joins. Always `dtype={"sid": str}` and `.str.zfill(11)`.

**5. Projected clips become chords in lat/lon.** Padding a clip window in lat/lon when
drawing in a conformal projection makes straight projected edges cut across the map.
Densify the boundary before transforming (`shapely.segmentize`).

**6. cfgrib exposes duplicate time coordinates.** For step-0 analyses both `time` and
`valid_time` are present and identical; renaming one creates an ambiguous merge key. Drop
`valid_time`.

**7. AIFS messages are not in chronological order.** A year's GRIB decodes out of order;
collect times per message and sort at the end. Also, don't open a 2,928-message file with
`cfgrib` — it indexes every message first. Iterate with eccodes directly and peak memory
stays flat (a full year crops in 7–12 s).

**8. The SYNOP temperature group cannot be found by regex.** `1sTTT` holds temperature,
but a search for `1\d{4}` also matches the `iihVV` visibility/cloud group — `11460`
decodes as **−46.0 °C** between readings of +2 °C. Locate it by position instead: scan
tokens from index 5 (past `AAXX`, date, station id, `iihVV`, `Nddff`), take the first
5-char token starting `1` whose second character is the sign 0/1, and stop at any
`2`-group. Discard section 3 (after ` 333`) first — it repeats groups with other meanings.

**9. OGIMET truncates responses at exactly 200,000 lines, station-major.** A truncated
reply loses the **high-numbered stations entirely** while still showing every day of the
period — so a day-coverage check passes and the loss is invisible. Only the exact line
count reveals it. Use ≤10-day windows and assert on the cap.

**10. Don't interpret a score before checking its sample count.** Two stations showed
ERA5 RMSE of 0.129 and 0.466 °C, below instrument precision, which looked like
assimilation contamination. They had **n = 2 and n = 1** paired observations. Require
n ≥ 100 before reading a per-station score.

**11. Condition jump checks on the actual time gap.** An apparent 17.5 °C 3-hourly jump
in SYNOP data was real data spanning a 6-hour reporting gap. Restricted to true
consecutive steps the maximum is 10.1 °C. An unconditioned `diff()` conflates a reporting
gap with a physical rate — and would have had me "fixing" a working decoder.

---

## 5. What the measurements say about modelling

**Use `ens_mean`, not `control`, as input.** Better at every lead beyond 0: by 0.234 °C at
+24 h, rising to 1.005 °C at +168 h. They are identical to three decimals at t+0.

**Feed the static fields, and condition on day-of-year.** Of the target's spatial pattern
(the domain mean is already right in the input), 13 % is a time-invariant map — exactly
what orography and a land–sea mask encode. But regressing the seasonal-mean pattern on
those fields shows the **land–sea coefficient reverses sign**: r = +0.557 in spring,
−0.621 in autumn. Physically, in spring the water is still cold and land warms first; by
autumn the water has stored heat and land cools first. One static map explains 13.2 % of
the pattern; four seasonal maps explain 22.6 %. So the static fields must enter as
**conditioning inputs the network modulates by day-of-year**, not as an additive offset.
(The fitted orography coefficient, −1.006 °C/100 m, sits close to the dry adiabatic lapse
rate — a sign the fit captures physics rather than noise.)

**Pass `lead_h` as a feature.** AIFS station error grows 1.24 → 3.11 °C from +0 to +168 h
and decomposes into a *non-growing* ~1.24 °C offset plus growth in quadrature. At +24 h
the non-growing term is still the larger of the two. Pooling leads averages over regimes
differing 2.5× in error magnitude.

**Report per lead and per season, never pooled.** Seasonal spread reaches 4× at long lead,
and pooling hides where the model actually helps.

### Baselines

Any model must beat interpolation. AIFS `ens_mean` bilinearly interpolated to the CERRA
grid, scored against CERRA (2025-07 → 2026-05):

| Lead | All | Winter | Spring | Summer | Autumn |
|---|---|---|---|---|---|
| +0 h | 1.318 | 1.231 | 1.297 | 1.670 | 1.135 |
| +24 h | 1.416 | 1.674 | 1.341 | 1.543 | 1.100 |
| +48 h | 1.550 | 1.827 | 1.480 | 1.683 | 1.207 |
| +72 h | 1.759 | 2.122 | 1.677 | 1.850 | 1.355 |
| +120 h | 2.411 | 3.143 | 2.262 | 2.200 | 1.810 |
| +168 h | 3.267 | **4.508** | 2.886 | 2.770 | 2.385 |

Winter is the hard regime, degrading 3.7× from t+0 to +168 h against 1.7× for summer.

And against **SYNOP station truth** — 83 well-sampled stations (39 Russian, 32 Finnish,
12 Estonian), 5 spatial folds, 2025-07 → 2026-05. The target box holds 85 SYNOP stations
(41 Russian); two Russian sites are excluded from per-station scores by the n ≥ 100
filter of trap 10:

| | RMSE (°C) |
|---|---|
| CERRA (5.5 km) | **1.076** |
| ERA5 (0.25°) | 1.475 |
| AIFS +0 h | 1.506 |
| AIFS +24 h | 1.664 |
| AIFS +72 h | 2.014 |
| AIFS +168 h | 3.347 |

Four readings:

- **The resolution gain is confirmed three times over, on three truth sources.** Headroom
  (ERA5 − CERRA) is **0.398 °C** on SYNOP, against 0.288 °C on 2020 ISD and 0.224 °C on
  IEM. It is positive at **93 % of stations and in every one of the 5 spatial folds**.
  The IEM figure was the low outlier because its 10 airport stations were mostly Finnish
  and Estonian, where the gain is smallest.
- **The gain is largest exactly where the project is aimed.** By country: Russia
  **0.514 °C**, Finland 0.364, Estonia 0.111. The earlier 10-station estimate had only
  2 Russian sites and so measured mostly the wrong region.
- **The stage-2 objective is 0.589 °C at +24 h** (1.664 → 1.076) — larger than the
  0.436 °C measured on IEM, because SYNOP includes the Russian stations where both the
  AIFS error and the CERRA advantage are bigger. At +168 h the gap is 2.27 °C but mostly
  forecast-error growth, which downscaling cannot fix; short leads are where this pays.
- **6 of 83 stations are ones where CERRA loses** to ERA5 — mostly Estonian coastal and
  Finnish lakeside sites. Worth watching, not alarming at 7 %.

> **CERRA carries a −0.19 °C cold bias against stations** while ERA5 is nearly unbiased
> (−0.02). A model trained to reproduce CERRA inherits that bias. Remove it at
> verification time, or the model will look colder than it is.

---

## 6. Coverage

| Sources | Window | Days |
|---|---|---|
| AIFS + CERRA + ERA5 + stations | 2025-07-01 → 2026-05-31 | **334** |
| AIFS ∩ CERRA (hard limits) | 2025-07-02 → 2026-05-31 | 334 |

2,673 valid times carry all four sources, holding **3,966** AIFS (init, lead) pairs. June
is absent by construction: CERRA ends 2026-05-31 and AIFS begins 2025-07-02.

**A piece of luck.** AIFS inits at 00/06/12/18 and CERRA analyses 3-hourly at 00/03/…/21
mean every 6-hourly-multiple lead lands exactly on a CERRA analysis time — 100 % of +24 h
valid times align. No temporal interpolation anywhere in the pipeline.

---

## 7. Scripts

| Script | Purpose |
|---|---|
| `build_station_truth.py` | ISD → 3-hourly truth. Handles the SYNOP/METAR trap |
| `build_station_truth_iem.py` | IEM → 3-hourly truth. Fahrenheit, nearest-report matching |
| `crop_cerra_multimsg.py` | Multi-message CERRA GRIB → cropped zarr. Memory-flat |
| `fetch_aifs_overlap.py` | AIFS extraction, per-init with immediate member reduction |
| `pair_aifs_cerra.py` | Stage-2 pairs with temporal folds |
| `pair_stations_cerra.py` | Station pairing with **spatial** folds |
| `compare_era5_cerra.py` | Three-way station comparison |

### Not yet built

- **Stage-1 pairing.** ERA5 2020 and CERRA 2020 both exist and are validated, but nothing
  writes them into the stage-2 array layout. Needs a GRIB→npz adapter, not new data. With
  ERA5 now held for 2025–26 as well, stage 1 could instead be built on the *same* period
  and truth source as stage 2 — a cleaner design that removes the ISD/IEM incomparability.
- **Model and training loop.** Input (5, 57, 116) — three AIFS channels plus `orog` and
  `lsm` — with `lead_h` and day-of-year as scalars, predicting (123, 127). A 5× linear
  upscale. Fits 4 GB VRAM comfortably at n = 3,240.

## 8. Standing caveats

- **Holdout must be spatial for any station claim.** Both ERA5 and CERRA assimilate this
  station network, so a temporal split makes station verification circular.
- **Point stations vs grid-box averages** is an irreducible error floor, largest at lake
  margins — precisely where the interesting signal is.
- **Station truth is treated as unified** across the three national networks (a deliberate
  simplification): no per-country bias correction, covariate, or stratified scoring.
  Revisit if residuals show a country-shaped spatial pattern.
- **2.5 km is an aspiration, not a target.** It sits below CERRA's own resolution, so
  there is no truth to verify it against.
- **CERRA assimilates ~2,100 SYNOP stations Europe-wide.** Our crop network is denser
  (~73 km spacing vs ~128 km), so some sites must be non-assimilated — but the station
  list is not published, so which ones cannot be determined.
