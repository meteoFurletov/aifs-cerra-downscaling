# The model, and how the data got to it

Two parts: the **provenance trail** (every transform from raw archive to training
array, with the shape at each step and the decision that shaped it) and the
**architecture ladder** (five candidate models, all actually fitted, with measured
skill).

Companions: `DATA.md` (sources and traps), `COMPARISONS.md` (what is scored against
what), `GRIDS.md` (the projection work), `domain_spec_leningrad.json` (every value).

---

## Part 1 — Data provenance

| Stage | Artifact | Shape | Reduction |
|---|---|---|---|
| AIFS ENS, raw archive | dynamical.org zarr | 1678 inits × 61 leads × 51 members × 721 × 1440 | — |
| AIFS extracted | `aifs_overlap.npz` | (667, 6, 3, 57, 116) | 209 MB |
| CERRA, raw | 2 GRIB files | 2680 msgs × 1069 × 1069 | 6.13 GB |
| CERRA cropped | `cerra_t2m_full.zarr` | 2680 × 123 × 127 | 87 MB |
| Static fields | `cerra_static_target.npz` | 2 × (123, 127) | 42 KB |
| **Stage-2 X** | `stage2_pairs.npz` | **(3240, 3, 57, 116)** | 257 MB |
| **Stage-2 Y** | `stage2_pairs.npz` | **(3240, 123, 127)** | 202 MB |
| Station truth | `station_truth_synop.parquet` | 717,034 obs × 299 sites | QC'd |
| Four-way paired | `synop_fourway.parquet` | 304,550 rows × 6 leads | — |

Each reduction was a decision, not a default:

**Domain: oblast + 100 km, extended until three lakes are whole.** A plain buffer left
Onega 82 % covered; whole lakes are the entire resolution argument, so the box grew north
for 10 % more cells. Cropping the *target* is free; cropping the *input* is not — air
advects 300–1700 km within the forecast range, so the input crop carries a 300 km margin.

**Members 51 → 3.** The store's chunks hold all leads and all members together, so reading
one member costs the same as reading all 51 — cost scales with *inits*, not members. So
read each init once and collapse immediately to (control, ensemble mean, spread). Storing
raw members would have been ~100× larger for no measured benefit; the ensemble mean beats
the control at every lead beyond 0.

**Leads 61 → 6.** 0/24/48/72/120/168 h. Every one is a multiple of 6 h, which lands
exactly on a CERRA analysis time — **no temporal interpolation anywhere in the pipeline.**

**Folds: 13 temporal blocks of 21 days, 5-day gaps.** The gap is measured, not guessed.
Raw autocorrelation is 0.82 at 21 days — that is the seasonal cycle, not predictability.
Deseasonalised and computed within a single init cycle (the 00/12 Z alternation aliases the
diurnal cycle otherwise), weather decorrelates to r ≈ 0.33 at 5 days. A 5-day gap costs
19 % of samples; 7 days costs 25 % to reach r = 0.20, which is not worth it at n ≈ 3,000.

> **These 13 folds are for the gridded loss only.** Any station-verified claim needs the
> *spatial* holdout, because both ERA5 and CERRA assimilate this station network and a
> temporal split would be circular.

**Station truth: SYNOP, not METAR.** The airport-only archive reached 10 of 86 stations
and disagreed with the historical archive by 0.57–1.35 °C — larger than the effect being
measured. Decoding raw synoptic bulletins reaches 85 of 86 including all 41 Russian sites,
and agrees with the historical archive to 0.009 °C because it is the same underlying
report.

---

## Part 2 — Architecture, by elimination

![Five models fitted; where the gain is, and where it is not]({{artifact:art_f12aa967-db99-4e5f-a2ed-c8684b863e07}})

Every rung below was **fitted and cross-validated**, not reasoned about. Gains are against
the interpolation baseline on the residual target.

| Rung | Model | Gain (°C) |
|---|---|---|
| 0 | interpolation, i.e. zero residual | 0.000 |
| 1 | per-lead constant offset | +0.003 |
| 2 | per-cell × lead climatology | +0.007 |
| 3 | per-cell linear, 10 local features | +0.034 |
| 4 | global ridge on 40 residual PCs | **−0.133** |
| 5 | **conv net, 39k params** | **+0.090** |

Rung 4 is the informative failure: 6,614 predictors against ~3,000 samples overfits so
badly it is *worse than doing nothing*. Rung 3 is the other bound — local features, however
many, cannot see a displaced front. **The answer has to have a spatial receptive field and
shared weights**, and that is a convolutional network. This is why, not an assumption.

Supporting evidence: the residual is strongly low-rank — 10 principal components carry
80 % of its variance, 50 carry 94 %. There is real structure to find; it is just not
findable per-cell or by an unregularised global fit.

### The chosen model

```
input   (3, 57, 116)  AIFS control / ens-mean / spread at native 0.25°
          ↓  3 dilated conv layers (d = 1, 2, 4), width 32   ← synoptic context
          ↓  grid_sample with the FIXED sampling grid          ← the regrid, differentiable
          ↓  concat orography + land-sea, FiLM-modulated by (sin doy, cos doy, lead)
          ↓  2 conv layers + 1×1 projection, zero-initialised
output  (1, 123, 127)  residual, added to bilinear(input)
```

**39,045 parameters.** Six design choices, each traceable:

1. **Residual form.** Target is `Y − bilinear(X)`: sd 2.06 °C against the full field's
   10.83 °C. Verified: the untrained model outputs **exactly 0.0**, so it *is* the
   interpolation baseline and cannot start worse.
2. **`grid_sample` inside the model.** The sampling grid is constant across all 3,240
   samples, so it is a buffer. No resampled copy on disk that can drift out of sync with
   the target grid, and the regrid is differentiable.
3. **Dilated convolutions, not a deep U-Net.** The residual decorrelates at 116–138 km
   = 21–25 cells; dilations 1/2/4 reach that in three layers without downsampling a
   57 × 116 input that cannot afford to lose resolution.
4. **Static fields as FiLM conditioning, not additive channels.** The land-sea thermal
   contrast *reverses sign* between spring and autumn, so a season-blind additive term
   averages two opposite regimes toward nothing.
5. **Width 32, not 128.** ~2,990 training samples per fold. Sample count is the binding
   constraint, not the 4 GB of VRAM.
6. **Huber loss, not MSE.** MSE on sharp land-water gradients drives blur, and a blurred
   field can score better on RMSE while being physically wrong.

### Where the gain actually is

**By surface** — this is the result that matters:

| | Interpolation | Conv net | Gain |
|---|---|---|---|
| **Ladoga area** | 2.621 | 1.848 | **+0.773** |
| Open water | 2.143 | 1.789 | +0.354 |
| Solid land | 1.926 | 1.881 | +0.045 |

**17× more gain over Ladoga than over land.** The model found exactly the signal the
spatial analysis predicted — sub-grid lake-land contrast — without being told where to
look. That is the strongest available evidence the architecture matches the physics.

**By lead**, the gain is roughly flat in absolute terms (+0.11 °C at t+0 falling to
+0.07 °C at +168 h) but shrinks sharply as a fraction: 6.8 % → 2.5 %. Consistent with the
earlier finding that short leads are representation-dominated and long leads are
forecast-error-dominated. **Report per lead; a pooled number describes no real forecast.**

### The honest caveat

High-wavenumber power in the prediction is **0.088 of the truth's** — the model is far
smoother than the field it predicts. It is winning on RMSE by being conservative, which is
exactly what an L2-family loss rewards. It has learned *where* the residual lives (the
lakes) but not its full amplitude.

This is the known failure mode of deterministic downscaling and it bounds what rung 5 can
claim: the current model improves accuracy, not realism. Fixing it means a loss that
penalises spectral mismatch, or a generative decoder — which is the next rung, and should
only be attempted now that a deterministic baseline exists to beat.

### What to do next, in order

1. **Extend to all 13 folds** — 3 were run; the fold-to-fold spread (+0.045 to +0.133 °C)
   is wide enough that 3 is not a stable estimate.
2. **Score against stations**, with the *spatial* holdout, via `verify_on_synop.py`. The
   gridded gain is necessary but not sufficient.
3. **Run the conservation check** — coarsen the model's output back to 0.25 ° with
   `esmf_roundtrip.py`. A model that improves station RMSE while failing this is
   redistributing heat, not resolving it.
4. **Add a spectral term to the loss** and re-measure the 0.088 power ratio. Only after
   1–3 pass.
5. **Then** consider capacity, individual members, or a diffusion decoder.
