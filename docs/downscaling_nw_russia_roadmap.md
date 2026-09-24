# Statistical downscaling for the Russian Northwest — orientation and roadmap

Scoping study, first session. Region: 55–70.5°N, 26–46°E (Pskov/Novgorod → Murmansk,
Baltic coast → Arkhangelsk/Vologda). Target: station-level post-processing of NWP output.

---

## 1. What is available (verified, not assumed)

**Station observations — NOAA ISD-Lite.** 299 Russian stations in the box; **144** with
≥15-year records still reporting into 2025. Verified variable coverage for 2024 at five
representative sites (Pulkovo, Valaam on Ladoga, Murmansk, Apatity in the Khibiny, Solovki):

| variable | coverage | usable |
|---|---|---|
| 2 m temperature | 99.8–100% | yes |
| 2 m dew point | 99.8–100% | yes |
| 10 m wind speed / direction | 99.2–100% | yes |
| sea-level pressure | 33–100% (station-dependent) | partially |
| cloud cover | 33–98% | partially |
| **precipitation (1 h and 6 h)** | **0%** | **no** |

Reporting frequency splits into two classes: ~8400 obs/year (hourly: Pulkovo, Murmansk)
and ~2750 obs/year (3-hourly: most rural sites). 11 of 144 stations are fully hourly.

> **Consequence for variable choice:** precipitation cannot be verified against this
> network at all. Any precipitation project needs a different truth source first
> (Roshydromet archives, satellite QPE, or ERA5-Land as a proxy) — that is a data-acquisition
> problem to solve *before* it is a modelling problem.

**Predictor / reanalysis fields — ARCO-ERA5.** Full ERA5 in cloud-optimised form, 1900→present,
0.25°, all 16 predictors we need present: `2m_temperature`, `2m_dewpoint_temperature`,
`10m_u/v_component_of_wind`, `surface_pressure`, `total_cloud_cover`, `boundary_layer_height`,
`snow_depth`, `surface_solar_radiation_downwards`, `total_precipitation`, `lake_cover`,
`lake_mix_layer_temperature`, `sea_surface_temperature`, `land_sea_mask`,
`geopotential_at_surface`, `forecast_albedo`.

*Access gotchas found:* statics must be read at a valid time index (`time=0` is year 1900 and
returns all-NaN); chunking is one **global** field per timestep (~4 MB), so download cost scales
with `n_times × n_vars` and is independent of how small your box is; 12-way concurrency times out
through the proxy — use ≤4 with retry.

**Forecast archives — dynamical.org.** ECMWF **AIFS ENS** and **IFS ENS**, both 51 members,
0.25°, identical grids. IFS archive is the deeper one (from 2024-04). Network access is granted;
the `dynamical-catalog` + `icechunk` packages still need installing.

---

## 2. The central finding: ERA5 is the wrong thing to downscale

I measured ERA5's own error against the 144 stations (25,822 matched pairs, 3-hourly,
25 Feb – 14 Apr 2024) and then tried to correct it with an honest chronological
70/30 train/test split.

**Baseline:** bias +0.08 K, MAE 0.90 K, **RMSE 1.31 K**.

![Error structure and correction skill]({{artifact:art_675e0ad3-b84f-4a30-b93f-638fcf49c776}})

Held-out skill of each correction, relative to raw ERA5:

| method | bias (K) | MAE (K) | RMSE (K) | skill |
|---|---|---|---|---|
| ERA5 raw (baseline) | +0.080 | 0.909 | 1.269 | — |
| + naive lapse rate (−6.5 K/km) | +0.189 | 0.922 | 1.286 | **−1.3%** |
| + per-station learned bias | +0.018 | 0.938 | 1.291 | **−1.7%** |
| + per-station × hour bias | +0.021 | 0.954 | 1.302 | **−2.6%** |
| GBDT, 15 predictors | −0.154 | 0.907 | 1.241 | **+2.2%** |

Three independent lines of evidence say the residual is essentially irreducible:

1. **Variance decomposition.** Across-station SD of systematic bias is 0.33 K against a
   1.31 K total — the structured, learnable part is only **~6% of the error variance**.
   Domain-mean bias is +0.08 K while mean *absolute* per-station bias is 0.27 K: the biases
   are real but they cancel, so no single global correction has anything to grip.
2. **Overfitting signature.** The GBDT drives training RMSE 1.33 → 0.82 K but gains only
   +2.2% out of sample. It is memorising noise, not learning physics.
3. **Error decorrelation.** Lag-1 autocorrelation of the error is 0.48 at 3 h, decaying to
   0.10 by 24 h — no persistent, predictable component to exploit.

**Why.** ERA5 *assimilates these very SYNOP stations*. Its analysis is already pulled onto them,
so its near-zero bias is partly circular. **Downscaling a reanalysis to its own input
observations has almost no headroom** — you are trying to beat a field that has already seen
the answer. The per-station biases that do exist track representativeness error, not model
error: station elevation minus ERA5 orography spans −128 to +72 m (σ = 29 m), and **15 of 144
stations sit on grid cells ERA5 calls water** (3 are lake cells, mean bias −0.29 K, mean RMSE
1.70 K — the worst class in the domain). Terrain mismatch alone correlates only r = 0.18 with
station bias, which is why the naive lapse-rate correction actively hurts.

*Caveat:* this rests on a 7-week late-winter/early-spring window. The conclusion about
assimilation circularity is structural and will hold, but the exact numbers should be
re-derived on a full annual cycle.

---

## 3. What to build instead

**Downscale forecasts, not reanalysis.** A +72 h IFS/AIFS ensemble forecast has *not* seen
tomorrow's observations. Its error is several times larger than ERA5's analysis error and a
large fraction of it is systematic and lead-dependent — that is real, correctable headroom.
ERA5's proper role in this project is as the **predictor/climatology source and the training
target's context**, not as the field being corrected.

This also reframes the goal usefully: the deliverable is a **station-level MOS/EMOS layer** that
takes ensemble forecast fields and emits calibrated point forecasts at all 144 stations —
which is exactly what an operational forecast desk would deploy.

### Recommended target variable: **2 m temperature first, 10 m wind second**

Reasoning from the evidence, not preference:

- **2 m temperature** — 100% observation coverage, best signal-to-noise, and the regional
  phenomena that coarse models genuinely miss (winter inversions and cold pools, the Ladoga/Onega
  and Gulf of Finland thermal contrast, the St. Petersburg heat island) are all temperature
  signatures. It is the right variable to learn the *method* on.
- **10 m wind speed** — also ~100% coverage, high practical value (Gulf of Finland, Ladoga,
  coastal Barents). Worth noting that prior work in this project overturned the expectation that
  wind is more defective than temperature over this domain; treat it as a second experiment, not
  an easy win.
- **Precipitation** — highest scientific interest (lake-effect snow off Ladoga/Onega is a real
  regional phenomenon) and prior work here found precipitation gives by far the biggest
  post-processing gains. But **the observations do not exist in this archive.** Defer until the
  truth-data problem is solved.
- **Fog / visibility** — weakest predictability, hardest verification. Not a starting project.

### Methods ladder, in the order worth climbing

1. **Nearest-gridpoint extraction + elevation correction** — establishes the baseline and
   teaches you the representativeness problem. Already prototyped.
2. **Per-station EMOS / non-homogeneous Gaussian regression** — the operational workhorse for
   ensemble temperature calibration: correct the mean *and* the spread, per station, per lead.
3. **Gradient-boosted trees on pooled stations** with terrain, land-sea fraction, lake cover and
   `dz` as predictors — lets one model serve all 144 stations and exploit spatial structure.
4. **Neural-network distributional regression with station embeddings** — the Rasp & Lerch
   approach, and the current reference standard for this exact task.

### Non-negotiable methodology

- **Three-way split (train / validation / test), seasonally balanced.** Fit parameters on train,
  select *only* on validation, score the final winner on test exactly once.
- Prior work in this project has a documented case where a method scoring **+4.2% on validation
  collapsed to −2.0% on test**. A two-way split will lie to you.
- Verify per lead time, not just in aggregate; the best method genuinely differs by lead.
- Baseline discipline: report skill against raw forecast *and* against per-station climatology.

---

## 4. Learning path

**Foundations (read alongside the build):**
- Rasp & Lerch (2018), *Neural Networks for Postprocessing Ensemble Weather Forecasts*,
  Monthly Weather Review — doi:10.1175/mwr-d-18-0187.1. The canonical paper for this task.
- Vannitsem et al. (2020), *Statistical Postprocessing for Weather Forecasts: Review,
  Challenges, and Avenues in a Big Data Era*. The field survey.
- Fiddes & Gruber (2014), *TopoSCALE v1.0: downscaling gridded climate data in complex
  terrain* — the physical/topographic route, useful contrast to pure ML.
- Muñoz-Sabater et al. (2021), *ERA5-Land*. Relevant if you pursue the precipitation branch.

**Concepts to be fluent in, in order:** representativeness error vs model error → CRPS and
proper scoring rules → reliability and rank histograms → spread/skill ratio →
EMOS/NGR → distributional regression → the difference between MOS and dynamical downscaling.

---

## 5. Immediate next steps

1. Install `dynamical-catalog` + `icechunk`; open the IFS ENS archive (the deeper one).
2. Build the matched forecast–observation cache: 144 stations × leads +24…+168 h,
   ≥12 months of initialisations, 2 m temperature. This is the asset everything else reuses.
3. Establish the raw-forecast baseline properly: bias, MAE, RMSE, CRPS, spread/RMSE ratio,
   rank histogram — **per lead**. Check spread vs RMSE *first*; if the raw ensemble is already
   well-dispersed, reach for bias correction and local methods rather than global EMOS.
4. Climb the methods ladder, logging every experiment against the three-way split.

**Open question to settle before step 2:** whether to pursue Roshydromet/RIHMI-WDC station data.
It would add precipitation and denser hourly reporting — the two things ISD-Lite lacks — and
would unlock the lake-effect snow problem, which is the most scientifically interesting target
in the region.
