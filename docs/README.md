# AIFS → CERRA downscaling, Leningrad Oblast — data phase complete

**Task.** Downscale ECMWF AIFS ENS 2 m temperature forecasts (0.25°) to the CERRA
regional reanalysis grid (5.5 km) over Leningrad Oblast + margin, and verify against
station observations.

**Status.** The data phase is closed. Every input, target and truth exists, is validated,
and restores from artifacts in one call. Stage-2 is trainable today. Stage-1 needs one
re-fetch (§5).

---

## 1. Start here

```python
from dataset import load_stage1, load_stage2, load_stations, check
d = load_stage2(host)              # X, Y, B, R, lead, fold, valid, orog, lsm, coords
d = load_stage2(host, aux=True)    # + 7 ERA5 predictor channels
d = load_stage1(host)              # ERA5 -> CERRA, 3-channel by default
st, obs = load_stations(host)
assert all(check(host).values())   # 15 assertions against documented values
```

**Five files, one per source.** Nothing derived is stored — pairing, the bilinear
baseline `B`, the residual `R = Y − B` and the fold assignment are all computed by
`dataset.py` on load, and `B` is cached to `_cache_B_stage{1,2}.npy` after the first
call (~25 s for both stages).

That is deliberate. Storing pre-paired training sets meant CERRA lived in three files at
once and they could silently disagree. Verified: the loader reproduces the old
the stage-2 set and the stage-1 set **exactly** — X bit-identical, Y/B/R to
1e-4 (float32 rounding), lead/fold/valid exact.

> Comparing the two requires sorting on **(valid, lead)**, not valid alone: 544 of 546
> valid times are shared by up to 6 different (init, lead) pairs, so valid is not a
> unique key for stage 2.

## 2. Documents, in reading order

| | |
|---|---|
| **`README.md`** | this file — index and closing state |
| **`DATA.md`** | every source, how it was obtained, and 10 traps that silently corrupt results |
| **`COMPARISONS.md`** | which comparison a number belongs to. **Read before quoting any RMSE** |
| **`GRIDS.md`** | lat/lon ↔ Lambert alignment, worked at St Petersburg; conservative regridding |
| **`MODEL.md`** | data provenance trail plus the fitted architecture ladder |
| `domain_spec_leningrad.json` | machine-readable: every constant, measurement and correction |

`COMPARISONS.md` is the one that prevents a real error: **CERRA is the truth in the
gridded comparison and a scored product in the station comparison.** Mixing the two
tables produces confident nonsense.

## 3. Canonical data artifacts

**521 MB total.** One file per source; each holds exactly what that source provides.

| File | Contents | Grid |
|---|---|---|
| `cerra.npz` 82 MB | `t2m` (2680, 123, 127) °C, 3-hourly analyses, no gaps · `time` · `lat`/`lon` · `orog` · `lsm` | target, 5.5 km |
| `era5.npz` 228 MB | `t2m` (2680, 57, 116) °C · `lake_ice_depth` · `lake_mix_layer_temp_C` · `lake_cover` · `snow_depth` · `skin_temp_C` · `u10` · `v10` · `time` · `lat`/`lon` | input, 0.25° |
| `aifs.npz` 209 MB | `cube` (667, 6, 3, 57, 116) °C, `field` = (control, mean, spread) · `init_time` · `lead_h` · `lat`/`lon` | input, 0.25° |
| `stations.parquet` 30 KB | 299 × 21 — sid, name, country, lat/lon/elev, role, spatial fold, per-station scores | — |
| `station_obs.parquet` 1.6 MB | 717,034 × 3 — sid, time, t2m_obs | — |

Assembled by `dataset.py` into 3,240 stage-2 pairs and 2,184 stage-1 pairs.

Kept alongside, not part of the training path: `station_truth.parquet` (2.19 M ISD
observations 2015–2024 — the only pre-2025 station data, needed if stage 1 is ever
extended back), `synop_fourway.parquet` (the four-way verification baselines in
`COMPARISONS.md`), and the two `esmf_*` files (the conservation-check record).

## 4. The numbers that matter

Measured over 2025-07 → 2026-05, 334 days, all four sources present.

| Against 83 SYNOP stations | RMSE |
|---|---|
| CERRA 5.5 km (the target) | **1.076 °C** ← floor; no model beats this |
| ERA5 0.25° | 1.475 °C |
| AIFS +24 h ens-mean | 1.664 °C |

- **Headroom = 0.400 °C** — what resolution buys, on truth. Replicated on 2020 with a
  different observation archive (0.288 °C).
- **Stage-2 objective = 0.588 °C** — AIFS(+24 h) minus CERRA.
- **Gridded baseline = 1.416 °C** at +24 h (2.065 °C pooled over all leads, a number that
  describes no real forecast situation — always report per lead).
- At the station cells the error decomposes exactly: **1.384 °C** downscaling gap +
  **1.076 °C** floor → **1.626 °C** experienced. About three quarters of the variance a
  user experiences at +24 h is in the part downscaling addresses.

## 5. Stage 1 — built

**ERA5 → CERRA, 2,184 pairs, 13 folds of exactly 168.** Both sides are analyses, so the
input carries no forecast error and the model learns the pure spatial operator.

| | Baseline RMSE |
|---|---|
| stage 1: ERA5 → CERRA | **1.236 °C** |
| stage 2: AIFS +0 h → CERRA | 1.318 °C |
| stage 2: AIFS +24 h → CERRA | 1.416 °C |
| stage 2: pooled all leads | 2.065 °C |

ERA5 was requested with `area=[67.0, 18.5, 53.0, 47.25]`, which reproduces the stage-2
input grid's 57 × 116 **exactly** — asserted against `src_lat`/`src_lon`, not assumed. All
2,680 CERRA analyses found a matching ERA5 valid time. 35.7 MB, ~3 min end to end.

`load_stage1(host)` returns the 3-channel form by default — the analysis repeated with
spread = 0, so the stage-2 architecture consumes it unchanged; pass
`three_channel=False` for the honest single-channel shape.

**Fold calendars are pinned to a shared epoch** (`FOLD_EPOCH = 2025-07-02`, stage 2's first
init). Fold *k* therefore covers the same dates in both stages, so pretraining on stage-1
folds ≠ *k* and testing on stage-2 fold *k* has zero overlap — verified, and now true by
construction rather than by luck. Before pinning, stage 1 anchored one day earlier and
leaked zero samples only because the 5-day gap absorbed the offset.

> **Stage 1 is easier than it looks, and this matters.** ERA5 → CERRA scores 1.236 °C
> against AIFS t+0 → CERRA's 1.318 °C, a gap that survives restricting both to the same
> 546 valid times (1.245 vs 1.318). The reason is structural: **CERRA is downscaled from
> ERA5** — ERA5 supplies its lateral boundary conditions — so the two share large-scale
> state by construction, while AIFS is an independent forecast. Stage-1 pretraining
> therefore sees a slightly optimistic operator, which is another reason stage 2 is not
> optional.

What would make stage 1 genuinely larger is **more CERRA years** (it runs 1984–2026), not
more ERA5 — and since CERRA has no area subsetting, each added year is a full-field
download through the browser.

## 5b. Auxiliary predictors, and two findings about how to read results

**`era5.npz`, aux fields** — 7 fields × 2,680 times on the stage-2 input grid, time axis identical
to `cerra.npz`: `lake_ice_depth`, `lake_mix_layer_temp_C`, `lake_cover`,
`snow_depth`, `skin_temp_C`, `u10`, `v10`. 285 MB of GRIB, folded into `era5.npz`.

Physically validated on Ladoga: ice 0.000 m Jul–Oct, 0.010 Dec, 0.187 Jan, **peak 0.566 m
Feb**, 0.087 Apr, 0.000 May; mixed-layer temperature 19.0 °C in August to 0.0 °C in
February. Correct freeze-thaw cycle.

**Why fetched.** The model's entire measured gain is over the lakes, and it had *no*
time-varying lake information — only static orography, a static land-sea mask, and
day-of-year. Calendar explains just 33 % of the Ladoga-minus-land residual contrast.

**What they are actually worth** — linear R² on that contrast, using window-mean scalars,
so a *lower bound* on what a convolutional model sees:

| Predictors | R² |
|---|---|
| calendar, 3 harmonics | 0.331 |
| + lake ice depth | 0.332 |
| + ice & mixed-layer temperature | 0.367 |
| + skin-temperature contrast & snow | 0.461 |
| + wind | 0.470 |

> **My hypothesis was wrong.** I expected lake ice depth to be the key variable. Alone it
> adds essentially nothing (0.331 → 0.332); the gain comes from the **skin-temperature
> contrast and snow depth**. Unexplained variance falls from 67 % to 53 % — real, but
> moderate, and less than the 67 % figure alone might suggest. `u10`/`v10` were included on
> physical grounds (advection direction decides which shore receives lake-modified air),
> not measured ones; they add 0.009 R². Treat wind as unproven.

### Finding: the folds are seasonally blocked

Folds 0–1 are pure summer, 2 autumn/summer, 3–5 autumn, **6–8 winter**, 9 spring/winter,
10–12 spring. Leave-one-fold-out therefore holds out a *season* — a harder and more honest
test than random splitting, but it means results must be reported per fold, never pooled.

**This changes how the reported model result must be read.** The +0.090 °C mean gain and
the +0.773 °C Ladoga gain were tested on folds 0, 1, 2 — 576 summer and 144 autumn samples,
**zero winter samples**. They are warm-season numbers. Winter is where the lake-land
contrast is largest (sd 1.702 °C) and least calendar-predictable, so it is the most likely
place for the estimate to move.

### Finding: one winter only

The 334-day span contains exactly one winter. Lake ice state and day-of-year are therefore
confounded — the model can memorise this winter's ice trajectory as a calendar function, and
inter-annual ice variability cannot be tested with one realisation. Fixing this needs more
CERRA years, at one full-field browser download each.

## 6. Standing constraints — do not relax these

1. **Two-stage ordering is required.** A model trained only on reanalysis pairs has learned
   its input is essentially correct, and will sharpen a displaced front confidently. The
   sharp wrong field is worse than the blurry one, because sharpness reads as skill.
2. **Station holdout must be spatial, not temporal.** Both ERA5 and CERRA assimilate this
   network. `stations.parquet` carries 5 spatially-contiguous folds. The 13 folds returned by
   `load_stage1`/`load_stage2` are temporal and are for the *gridded* loss only.
3. **Never pool the two station archives**, or cross-score one against the other's
   baseline. They disagree by 0.57–1.35 °C, more than several measured effects.
4. **Report per lead and per season.** Seasonal spread reaches 4× at long lead; the lake
   signal inverts sign with lead. Pooling hides both.
5. **Report maps, not just scalars.** Per-cell RMSE varies 2.4× across the domain.
6. **Nearest cell for stations, bilinear for fields.** The gridded fields are grid-box
   averages; interpolating to a point invents values the dataset never claimed.
7. **Never issue an exploratory CDS request while a real job is pending** — the per-user
   limit on the MARS-backed archive is 1, so a probe consumes the slot.

## 7. What the data says about the model

Fitted and cross-validated, gains against the interpolation baseline:

| Model | Gain |
|---|---|
| per-cell linear, 10 local features | +0.034 °C |
| global ridge on 40 residual PCs | **−0.133 °C** (overfits: 6.6k predictors, 3k samples) |
| conv net, 39k params | **+0.090 °C** |

Those two failures pin the architecture from both sides: it needs a spatial receptive field
*and* shared weights. The conv net gains **+0.773 °C over Ladoga against +0.045 over
land** — it found the sub-grid lake signal without being told where to look.

Open caveat: high-wavenumber power in the prediction is 0.088 of the truth's. The model
improves accuracy, not realism. See `MODEL.md` §"honest caveat".

## 8. Environments

| Env | Contains |
|---|---|
| `downscale` | the working environment — xarray, cfgrib, eccodes, pyproj, cartopy, zarr |
| `downscale-esmf` | + `xesmf` / `esmpy`. Needs `ESMFMKFILE`; `esmf_roundtrip.py` sets it itself |
| `downscale-torch` | + `torch` (CUDA available on the local 1650 Ti) |

Kept separate deliberately: ESMF and torch are both heavy and neither is needed for data
work.
