# What is compared to what

Every number this project has produced belongs to one of **three distinct comparisons**.
They use different truth, different populations, and different sample sizes — and in one
of them CERRA is the *truth*, while in another CERRA is a *thing being scored*. Quoting a
number without naming its comparison is how this project would mislead itself.

This document is the registry. Companion documents: `DATA.md` (what the datasets are,
where they came from, and the traps in them) and `domain_spec_leningrad.json`
(machine-readable, every value below).

![The three comparisons, and how the errors decompose]({{artifact:art_fa0b37ef-961f-4a0d-a64b-d6ddcb195872}})

---

## 0. The four objects

| | What it is | Grid | Role |
|---|---|---|---|
| **AIFS ENS** | ECMWF AI ensemble *forecast*, 51 members | 0.25° (27.8 × 13.9 km at 60 °N) | model **input** |
| **ERA5** | global reanalysis *analysis* | 0.25° | stage-1 input; also AIFS's training data |
| **CERRA** | regional reanalysis *analysis* | 5.5 km Lambert | model **target** |
| **SYNOP stations** | point observations, 83 sites | points | independent **truth** |

The forecast/analysis distinction is the one that matters. AIFS is a forecast and carries
real forecast error that grows with lead time. ERA5 and CERRA are analyses — they saw the
observations, so they have no lead time and their error is flat.

---

## 1. Comparison A — the gridded comparison

**`bilinear(AIFS ens-mean)` vs `CERRA field`, over all 15,621 target cells.**

This is the one that defines the modelling task. It asks: how far is a coarse forecast,
naively interpolated onto the fine grid, from the fine analysis we want it to look like?

- **Prediction:** AIFS ensemble mean at lead L, bilinearly interpolated 0.25° → 5.5 km
- **Truth:** CERRA analysis at the same valid time
- **Population:** 3,240 field pairs × 15,621 cells = **50.6 M cell-values**
- **Where:** `stage2_pairs.npz` (`X` → `Y`), baseline in `stage2_baseline_interp.csv`

| Lead | RMSE (°C) |
|---|---|
| +0 h | 1.318 |
| +24 h | 1.416 |
| +48 h | 1.550 |
| +72 h | 1.759 |
| +120 h | 2.411 |
| +168 h | 3.267 |

**This is the number a model must beat.** A residual-form model with zero output reproduces
it exactly, so it is both the baseline and the floor for "did the model do anything".

> **CERRA is the truth here.** Its own error against real observations does not appear in
> this comparison at all. A model can score perfectly on comparison A and still be wrong
> about the weather, because it would only have learned to reproduce CERRA.

---

## 2. Comparison B — the station comparison

**Each gridded product vs `SYNOP point observations`, at 83 stations.**

This is the one that says whether any of it is true. All three products are scored against
the same independent truth, on identical samples.

- **Prediction:** nearest grid cell of each product (no interpolation — the fields are
  grid-box averages, so interpolating invents values)
- **Truth:** SYNOP observations, 2025-07 → 2026-05
- **Population:** **51,187 station-times per lead**
- **Where:** `synop_fourway.parquet`, summary in `synop_summary.csv`

| | RMSE (°C) | Has lead time? |
|---|---|---|
| **CERRA (5.5 km)** | **1.076** | no — analysis |
| **ERA5 (0.25°)** | **1.475** | no — analysis |
| AIFS +0 h | 1.506 | yes |
| AIFS +24 h | 1.664 | yes |
| AIFS +72 h | 2.014 | yes |
| AIFS +168 h | 3.347 | yes |

Three quantities come out of this table, and they are different things:

**Headroom = ERA5 − CERRA = 0.400 °C.** What resolution buys, measured on truth. This is
the justification for the whole project: a 5.5 km analysis really is closer to reality
than a 0.25° one, by an amount worth chasing.

**The stage-2 objective = AIFS(+24) − CERRA = 0.588 °C.** How far a real forecast sits from
the target's quality. This is what fine-tuning has to close.

**The floor = CERRA vs stations = 1.076 °C.** No downscaling model can beat this, because
it is the target's own distance from reality. It combines CERRA's analysis error with the
point-vs-grid-box mismatch — a 5.5 km cell average is not a thermometer reading.

> **Here CERRA is being scored, not used as truth.** That is the exact inversion of
> comparison A, and the reason these two tables must never be mixed.

---

## 3. Comparison C — the historical station comparison

**ERA5 and CERRA vs `ISD observations`, 86 stations, 2020 only.**

Same structure as B but a different year and a different observation archive. Its value is
*replication*: it was measured before the 2025–26 data existed.

- **Truth:** NOAA ISD, 2020, 86 stations
- **Population:** 212,268 station-times
- **Where:** `three_way.parquet`

| | RMSE (°C) |
|---|---|
| CERRA | 0.875 |
| ERA5 | 1.164 |
| **headroom** | **0.288** |

> ISD and SYNOP disagree by 0.57–1.35 °C at shared stations (`DATA.md` trap 2), so
> **absolute values from B and C are not comparable**. The *headroom*, being a difference
> of two products against the same truth, is comparable — which is what makes the
> replication meaningful.

---

## 4. How the three fit together

At the station cells, on one identical set of 42,210 rows at +24 h, the errors decompose
exactly (`|a + c − total| < 1e-15`):

```
AIFS  ──1.384 °C──▶  CERRA  ──1.076 °C──▶  station truth
  └──────────────── 1.626 °C ────────────────┘
```

- **1.384 °C** is the downscaling gap — comparison A's quantity, restricted to station
  cells. **This is what a model can reduce.**
- **1.076 °C** is the floor — comparison B's CERRA row. **No model touches this.**
- **1.626 °C** is what a forecast user actually experiences.

The quadrature sum would be 1.753 °C, but the experienced error is 0.127 °C *below* that,
because the two error terms are slightly anti-correlated (r = −0.119). Variance shares are
therefore 72 % downscaling gap and 44 % floor — which exceed 100 % precisely because of
that cancellation, not because of an arithmetic error.

**The practical reading:** roughly three quarters of the error variance a user experiences
at +24 h is in the part downscaling addresses. That is the strongest single argument for
doing this work, and it only becomes visible once the three comparisons are separated.

---

## 5. The spatial comparison

Comparison A resolved per cell instead of averaged, with comparison B's stations as
independent confirmation.

**Surfaces** (open water = land-sea mask < 0.05; solid land > 0.95; the 20 % of cells in
between are a distinct shore class — thresholding a fractional mask at 0.5 washes the
signal out entirely and gave a wrong "no difference" answer on the first attempt):

| Surface | Cells | t+0 | +24 h | +168 h |
|---|---|---|---|---|
| Open water | 1,720 (11 %) | 1.435 | **1.732** | 2.741 |
| Mixed shore | 3,135 (20 %) | 1.211 | 1.417 | 3.278 |
| Solid land | 10,766 (69 %) | 1.297 | 1.323 | 3.324 |

**Per lake, at +24 h:** Onega 2.177 (1.64× land), Ladoga 1.935 (1.46×), Gulf of Finland
1.383 (1.05×). The inland lakes carry the error; the marine Gulf behaves almost like land.

**The lake penalty inverts with lead** — 1.22× at t+0, peaking at **1.52× at +24 h**, then
1.00× at +120 h and 0.87× at +168 h. At short lead the error is representation: the coarse
input cannot resolve a real lake–land thermal contrast. At long lead the error is synoptic
placement, and a large thermally-inert lake is a *more* predictable surface than
heterogeneous land. **So the lake-effect claim is a short-lead claim — target ≤ +72 h.**

**Comparison B confirms it independently.** Station headroom is +0.718 °C within 15 km of
Ladoga/Onega and +0.682 °C at 15–40 km, against +0.355 °C beyond 80 km — it doubles. And
it correlates with distance to those two lakes (r = −0.43) but not to water in general
(r = −0.06), so the effect is the big lakes specifically, not coastlines.

**One unexplained pattern:** a northeastward error gradient, correlating +0.48 with
latitude and +0.41 with longitude but **+0.009 with orography** and +0.06 with the
land-sea mask. Present already at t+0, so it is representation error rather than forecast
growth. Since the static fields do not explain it, a coordinate channel may help the model
absorb it.

---

## 6. Rules for quoting these numbers

1. **Name the comparison.** "RMSE 1.4 °C" is meaningless; "comparison A at +24 h" is not.
2. **Never mix A and B.** CERRA is truth in one and scored in the other.
3. **Never compare absolute values across B and C.** Different observation archives,
   differing by more than several measured effects. Headroom *is* comparable.
4. **Report per lead and per season, never pooled.** Seasonal spread reaches 4× at long
   lead; pooling hides where the model helps. Comparison A pooled over all leads is
   2.065 °C, a number that describes no real forecast situation.
5. **Report maps, not just scalars.** Per-cell RMSE varies 2.4× across the domain.
6. **A model beating comparison A has not been validated.** It has only learned to
   reproduce CERRA. Validation requires comparison B, with the spatial holdout — both
   ERA5 and CERRA assimilate these stations, so a temporal split would be circular.

## 7. Provenance note

AIFS is extracted two ways in this project: bilinearly onto the CERRA grid (comparison A)
and by nearest 0.25° cell (comparison B). At the station points the two differ by mean
+0.006 °C, sd 0.367 °C, and change AIFS-vs-station RMSE from 1.672 to 1.626 °C. The choice
is immaterial to every conclusion here, but the 1.664 °C in comparison B's table is the
nearest-cell figure, computed over all leads' station-times rather than the +24 h subset
used in the §4 decomposition — which is why §4 shows 1.626 °C for the same nominal
quantity.
