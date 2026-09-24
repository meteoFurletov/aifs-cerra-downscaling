# AI Weather Forecast Models: Architectures, Defects, and What Already Exists for AIFS

**Track:** AI/ML weather forecast model landscape and its known failure modes
**Scope:** 63 verified references. Retraction status checked across the full retrieved pool (761 records) — none retracted.
**Purpose:** establish what AIFS is, what it gets wrong, and whether anyone has already downscaled it.

A note on reading this: every claim below is attributed to a specific paper. Where a number appears, it
is the number that paper states. Where the literature is thin or silent, that is said explicitly rather
than filled in.

---

## 0. The one-paragraph answer to the question that matters

**AIFS downscaling is NOT unoccupied ground.** Four distinct pieces of work already post-process or
downscale AIFS output, three of them from 2026. A national met service has run its existing operational
post-processing system on AIFS unmodified and found it works (Trotta et al. 2025, 10.1175/aies-d-25-0037.1);
a Swiss group has done lead-time-aware bias correction plus generative super-resolution of AIFS precipitation
to kilometre scale (arXiv 2605.16163); a Norwegian group has built a probabilistic *temporal* downscaler
for AIFS-Single and AIFS-ENS (arXiv 2607.11457); and a Shanghai group has a diffusion emulator taking AIFS
to km-scale regional fields (10.1029/2025jh001072). Separately, ECMWF's own architecture has been extended
into a stretched-grid regional model at 2.5 km over the Nordics (arXiv 2409.02891, 2511.23043).

This is good news, not bad. It means the approach is validated, the methods are published, and the
remaining gap is *geographical and methodological* rather than conceptual — see §5.

---

## 1. Architectures: what these models actually are

### 1.1 The one you care about — AIFS

**AIFS (Lang et al. 2024, arXiv 2406.01465, preprint, 73 citations).** ECMWF's data-driven forecasting
system. Architecture is a **graph neural network encoder and decoder with a sliding-window transformer
processor** — this hybrid is the distinguishing choice; it is not a pure transformer like Pangu nor a pure
GNN like GraphCast. Trained on **ERA5 reanalysis plus ECMWF's operational NWP analyses**. Modular, with
several levels of parallelism to permit high-resolution training. The paper reports skill for upper-air
variables, surface weather parameters and tropical cyclone tracks, verified against both analyses *and
direct observational data*. Crucially for you: **run four times daily and available publicly under
ECMWF's open data policy.**

**AIFS Single update (Moldovan et al. 2025, arXiv 2509.18994, preprint).** Read this second — it tells you
what version you are actually downloading. Adds **physical-consistency constraints via bounding layers**,
an updated training schedule, and an expanded variable set. States the bounding layers **substantially
improve precipitation forecasts**. Confirms **AIFS has been fully operational at ECMWF since 25 February
2025.** The version matters: a downscaling model trained on pre-bounding-layer AIFS precipitation is
learning to correct a defect that has since been partly fixed upstream.

**AIFS-CRPS (Lang et al. 2026, npj Artificial Intelligence, 10.1038/s44387-026-00073-7, 11 citations;
preprint arXiv 2412.15832).** This is the ensemble you would downscale. The innovation is the loss: an
**"almost fair CRPS"**, which approximately removes the finite-ensemble-size bias in the score while
avoiding the degeneracy of the fair CRPS. The consequence is a model trained *directly* to be probabilistic
rather than an ensemble assembled from perturbed deterministic runs. Result: for medium range it
**outperforms the physics-based IFS ensemble for the majority of variables and lead times**; for
sub-seasonal it beats IFS ENS before calibration and is competitive after anomaly transformation.
The methodological lesson generalises — CRPS-type training is the standard for generative ensembles now.

**The AIFS family is expanding, and two members are directly relevant to your constraints:**

- **AIFS-DOP (arXiv 2606.19093, preprint):** end-to-end prediction **from observations alone**, no
  reanalysis in the loop. Given your established finding that ERA5 assimilates the very SYNOP stations you
  validate against, an observation-trained model changes the verification logic fundamentally. Worth
  watching even if not yet usable.
- **AIFS-SUBS (arXiv 2607.05100, preprint):** sub-seasonal, 24 h autoregressive step to limit error
  accumulation, adds stratospheric levels and top-of-atmosphere thermal radiation.
- **AIFS ocean/wave/sea-ice coupling (arXiv 2604.25559)** matters for the marine margins of your box
  (Gulf of Finland, White Sea, Barents).
- **AIFS-COMPO (arXiv 2604.03300)** — atmospheric composition. Listed to show the Anemoi/AIFS codebase is
  a genuine ecosystem you can build on rather than a single frozen model.

### 1.2 The comparison set

| Model | Primary reference | Resolution | Det. vs ens. | Notable |
|---|---|---|---|---|
| **GraphCast** | Lam et al. 2023, Science, 10.1126/science.adi2336 (1300 cit.) | 0.25° | Deterministic | GNN on multi-mesh; beat operational deterministic on 90% of 1380 verification targets; sub-minute inference |
| **Pangu-Weather** | Bi et al. 2023, Nature, 10.1038/s41586-023-06185-3 (1543 cit.) | 0.25° | Deterministic | 3D Earth-Specific Transformer; hierarchical temporal aggregation to limit autoregressive error growth |
| **FourCastNet** | Pathak et al. 2022, arXiv 2202.11214 (preprint, 453 cit.) | 0.25° | Det. (cheap ensembles) | Adaptive Fourier Neural Operator; week-long forecast in under 2 s — the "large ensemble for free" argument |
| **FourCastNet 3** | Bonev et al. 2025, arXiv 2507.12144 (preprint) | 0.25° | Probabilistic | Geometric/spherical-signal-processing approach; **retains realistic spectra out to 60 days**; 60-day forecast in <4 min on one GPU |
| **GenCast** | Price et al. 2024, Nature, 10.1038/s41586-024-08252-9 (355 cit.) | 0.25°, 12 h steps | Diffusion ensemble | 15-day ensemble in 8 min; better than ENS on **97.2% of 1320 targets** |
| **NeuralGCM** | Kochkov et al. 2024, Nature, 10.1038/s41586-024-07744-y (384 cit.) | ~140 km for climate runs | Hybrid | Differentiable dynamical core + learned physics; stable multi-decade integrations |
| **FuXi-ENS** | Zhong et al. 2025, Sci. Adv., 10.1126/sciadv.adu2854 | 0.25° | CRPS-trained ensemble | Independent line converging on the same CRPS-training idea as AIFS-CRPS |
| **Huge Ensembles (SFNO)** | Mahesh et al. 2025, GMD, 10.5194/gmd-18-5575-2025 (10 cit.) | 0.25° | Very large ensemble | 1.1 B params; see §2.1 — its spectral diagnostic is the important part |

**Baseline framework:** WeatherBench 2 (Rasp et al. 2024, JAMES, 10.1029/2023ms004019, 195 citations) defines the metrics and provides
the baseline data. Read it before you verify anything, so your numbers are comparable to published ones.

### 1.3 Why the architecture choice matters for you

All the global models above sit at **0.25° nominal** (~28 km at the equator, ~12 km east-west at 65 °N —
your latitudes get a *finer* zonal grid spacing but the same physical smoothing scale). Nominal grid
spacing is not effective resolution (§2.2). A GNN-based model like AIFS is the easiest to extend
regionally, because a graph naturally supports arbitrary multi-resolution grids — which is exactly the
route the Nordic stretched-grid work took (§4).

---

## 2. Known error modes — the defects a downscaling layer would target

This is the substantive part. Each subsection states the defect, the evidence, and the implication for a
station-level downscaling project in NW Russia.

### 2.1 Spatial over-smoothing / blurring

**The canonical statement (Bonavita 2024, GRL, 10.1029/2023gl107377, 136 citations; preprint arXiv
2309.08473).** Examining Pangu-Weather, FourCastNet and GraphCast: the main conclusion is that these models
**"are not able to properly reproduce sub-synoptic and mesoscale weather phenomena and lack the fidelity
and physical consistency of physics-based models"**, and that this affects both the interpretation of their
forecasts and their *perceived* skill. That last clause is the deep point: RMSE-optimal forecasts are
blurred forecasts, so a model can win on RMSE precisely by being unphysically smooth. This is the
single most important defect paper in the track.

**A clean quantification (Luitel et al. 2026, arXiv 2607.11905, preprint).** GraphCast over the Indian
summer monsoon: regional power-spectrum **variance ratio of 0.14 against IMERG** — i.e. the model retains
roughly a seventh of the observed small-scale variance — with a compressed rainfall intensity distribution.
A different region and variable from yours, but it is the kind of number that makes the defect concrete.

**The critical refinement (Mahesh et al. 2025, GMD, 10.5194/gmd-18-5575-2025).** ML ensemble **members**
maintain approximately constant power spectra with lead time, while the ensemble **mean** degrades. Read
this carefully, because it reframes the whole problem: blurring is not necessarily intrinsic to the
architecture — it is what averaging does, and what MSE training incentivises. If you downscale the AIFS
ensemble *mean* you are downscaling a smoothed field; if you downscale *members* you are not.

**The counter-example (Bonev et al. 2025, FourCastNet 3, arXiv 2507.12144).** Retains realistic spectra
out to 60 days. Together with the point above, this means "AI models blur" is a statement about training
objectives, not about neural networks.

**Implication for you:** downscale ensemble members, not the mean. And if you build a learned downscaler,
an MSE loss will reproduce the very defect you are trying to fix — see §4.2 for the spectral-loss finding.

### 2.2 Effective resolution below nominal grid spacing

**Brenowitz et al. 2025 (GRL, 10.1029/2024gl113656, 23 citations; preprint arXiv 2401.15305).** A practical
probabilistic benchmark for AI weather models. The load-bearing result: SFNO ablations that modulate
**effective resolution** show it has **a useful effect on ensemble dispersion relevant to achieving good
ensemble calibration**. This is the explicit link between the blurring defect and the under-dispersion
defect — they are not independent problems.

**Rodwell et al. 2025 (Meteorological Applications, 10.1002/met.70071).** Power spectra of physics-based
and data-driven ECMWF ensembles, giving the diagnostic toolkit. For physics-based ensembles, extratropical
250 hPa geopotential variance saturates quickly at small scales while planetary-scale errors remain far
from saturated at day 10, and at intermediate lead times the forecasts are **over-dispersive at synoptic
scales**. Useful as the reference against which data-driven spectra should be judged — note the physics
model has its own dispersion errors, so "AI is under-dispersive" needs a fair baseline.

**Implication:** compute your own spectra before and after downscaling. It is cheap, it is the standard
diagnostic in this literature, and re-coarsening consistency (§3.4) is its natural companion check.

### 2.3 Behaviour in extremes and the distribution tails

Three papers, and they disagree in an informative way.

**Olivetti & Messori 2024 (GMD, 10.5194/gmd-17-7915-2024, 26 citations).** Comparing IFS HRES,
Pangu-Weather and GraphCast on near-surface temperature and wind speed extremes globally: data-driven
models **mostly outperform** the physics-based deterministic model on global RMSE at 1–10 days and can
compete on extremes in most regions. But — and this is the part relevant to you — **performance varies by
region, type of extreme, and lead time**, and the models **perform best for temperature extremes in
regions closer to the tropics and at shorter lead times**. Your domain is 55–70.5 °N. Do not assume
published global skill numbers transfer to it.

**Zhang et al. 2026 (Science Advances, 10.1126/sciadv.aec1433, 3 citations; preprint arXiv 2508.15724).**
For **record-breaking** extremes, IFS HRES **still consistently outperforms** GraphCast, GraphCast
operational, Pangu-Weather, Pangu-Weather operational and FuXi. The AI models **underestimate both the
frequency and the intensity of record-breaking events**, and specifically **underpredict hot records while
overpredicting cold records, with errors growing for larger record exceedance**. That asymmetry is a
systematic, correctable bias — precisely the kind of thing a tail-aware post-processor targets.

**Gabler et al. 2026 ("Do AI weather models miss extremes?", arXiv 2608.09972, preprint) — the most
directly relevant error-mode paper for your setup**, because it verifies against **stations** rather than
reanalysis, over Europe, across 11 forecast systems and 10 months. Two findings: (i) **AIFS loses
4.9 ± 2.0% in the heat tail** — a model-specific, quantified tail penalty; and (ii) **all systems,
including the physics-based NWP ones, show a shared conditional bias toward the centre of the
distribution.** Conclusion: tail failure is not a uniquely-AI pathology, it is a regression-to-the-mean
property of forecast systems generally. Your downscaler should be evaluated with this in mind, and
station-based verification is the right frame.

### 2.4 A climatological bias from training on history

**Landsberg et al. 2026 (GRL, 10.1029/2025gl119740, 1 citation; preprint arXiv 2509.22359).** Boreal-winter
land temperature biases in FourCastNet V2 Small, Pangu-Weather and the ACE2 climate emulator, evaluated on
periods substantially more recent than the bulk of their training data. **All models are cold-biased,
resembling climates 15–20 years earlier than the period being predicted** — in some regions such as the
eastern US, 20–30 years earlier. FourCastNet's and Pangu's cold bias is **strongest for the hottest
predicted temperatures**, attributed to limited training exposure to modern extreme heat.

**Implication, and it is a sharp one for your project:** this bias is inherited from training-data recency,
so a downscaler trained on a historical archive will *learn the stale climatology as if it were truth*.
Two consequences: (a) prefer recent training windows and check for drift; (b) boreal winter over land is
exactly your regime, so this is not a distant concern. Note the paper does not test AIFS — that is a gap
(§5).

### 2.5 Physical consistency and conservation

- **Bonavita 2024** (above) — lack of physical consistency is one of its two headline conclusions.
- **AIFS Single update (arXiv 2509.18994)** — ECMWF's response: bounding layers imposing physical
  constraints, which "substantially improve precipitation forecasts". Evidence the field is actively
  patching this.
- **Kim et al. 2026 (npj Clim. Atmos. Sci., 10.1038/s41612-026-01380-1, 2 citations)** — a
  spectral test of the butterfly effect and physical consistency in diffusion-based GenCast ensembles.
  This is how you test whether a *generative* ensemble perturbs the atmosphere realistically rather than
  just adding decorative noise. Directly applicable if you use a diffusion downscaler.
- **Slivinski et al. 2025 (GRL, 10.1029/2024gl114396, 14 citations)** — assimilating surface pressure into ML models produces noise
  requiring spectral filtering. Evidence ML models are brittle to off-manifold inputs. Relevant if you ever
  feed station observations back into a model.
- **Charlton-Perez et al. 2024 (npj Clim. Atmos. Sci., 10.1038/s41612-024-00638-w, 67 citations)** —
  "Do AI models produce better weather forecasts than physics-based models?", a quantitative Storm Ciarán
  case study. The standard single-event reference for AI models capturing synoptic structure while missing
  smaller scales.

### 2.6 Near-surface and land-surface specifics

This is where the literature is **thinnest**, and it is worth stating plainly.

- **Wesselkamp et al. 2025 (GMD, 10.5194/gmd-18-921-2025, 11 citations)** — LSTM vs gradient boosting vs
  MLP as ecLand land-surface emulators. Doubly relevant: your box is snow- and boreal-surface dominated,
  and it benchmarks exactly the model classes that fit on 12 cores and a 4 GB GPU.
- **Sha et al. 2020 (JAMC, 10.1175/jamc-d-20-0057.1, 148 citations)** — deep-learning gridded downscaling
  of daily Tmax/Tmin in **complex terrain**. The closest classical treatment of the elevation/
  representativeness problem you already measured (station-minus-model orography spanning −128 to +72 m).
- **Ben Bouallègue et al. 2024 (BAMS, 10.1175/bams-d-23-0162.1, 159 citations)** — ECMWF's own first
  statistical assessment of ML forecasts in an operational-like context. The reference for how these
  models behave in operations as opposed to in benchmark papers.
- **Beucler et al. 2025 (AIES, 10.1175/aies-d-24-0078.1)** — "Distilling Machine Learning's Added Value:
  Pareto Fronts"; a framework for deciding whether ML added value justifies its cost and complexity. A useful discipline for a solo project with finite compute.
- **Bröcker et al. 2026 (J. European Meteorological Society, 10.1016/j.jemets.2026.100032)** — what
  verification of AI-based environmental forecasting systems can and needs to do, and the challenges. Read
  before designing your evaluation, not after.
- **Extreme Weather Bench (McGovern et al. 2026, arXiv 2605.01126, preprint)** — a community framework and
  benchmark for high-impact weather. Adopt rather than invent.

**I found no paper specifically evaluating AI weather models over NW Russia, the Barents/White Sea region,
or high-latitude European Russia.** Targeted searches for Arctic/Nordic/Baltic/Russia-specific AI-model
verification returned nothing on-topic. Likewise, no paper isolating AI-model behaviour in the
**stable boundary layer** or under **snow cover** — the two regimes that dominate winter 2 m temperature
error at your latitudes. This is a real gap, not a search failure (§5).

---

## 3. AIFS-specific post-processing and downscaling — what exists

### 3.1 The direct precedent: operational post-processing applied to AIFS unchanged

**Trotta et al. 2025 (AIES, 10.1175/aies-d-25-0037.1; preprint arXiv 2504.12672). Read this first among
the application papers.** The Australian Bureau of Meteorology applied **IMPROVER, its existing operational
statistical post-processing system**, to ECMWF's deterministic AIFS, comparing against post-processed HRES
and ENS. Findings, in the paper's own framing: AI models reach operational-grade performance for some
variables but, **like traditional NWP models, exhibit systematic biases and reliability issues**;
**without any modification to processing workflows**, post-processing yields **comparable accuracy
improvements for AIFS as for traditional NWP** in both expected-value and probabilistic outputs; and
**blending AIFS with NWP models improves overall skill even when AIFS alone is not the most accurate
component.**

Three things follow for you. First, your project is *validated by precedent* — a national met service did
essentially the thing you propose and it worked. Second, **you do not need AI-specific methods**; the
classical post-processing toolkit transfers. Third, **blending beats picking** — your baseline should
include an AIFS+IFS blend, not AIFS alone. (Both archives are available to you at 0.25°, 51 members.)

### 3.2 Generative super-resolution of AIFS precipitation

**SwAIther-Precip (Assouline et al. 2026, arXiv 2605.16163, preprint).** Lead-time-aware bias correction
enabling kilometre-scale generative downscaling of AIFS precipitation over Switzerland. The closest
existing analogue to your stated idea. Reported: **CRPS reduced 48% versus raw AIFS**; **effective
resolution ~4 km on a 1 km target grid** (note the honesty — nominal 1 km, effective 4 km, exactly the
distinction from §2.2); and **training jointly across lead times yields a further 13% CRPS gain at day 6**
relative to per-lead-time training. That last number is a transferable design lesson: lead-time-aware
training is worth real skill.

Caveat for your domain: this is precipitation over Switzerland with a dense radar/gauge target. **Your
ISD-Lite archive has 0% precipitation coverage**, so the target field for a precipitation analogue does
not exist in your data. Temperature and wind are where your data supports you.

### 3.3 Temporal downscaling of AIFS, including the ensemble

**HourGlass (Ingstad et al. 2026, arXiv 2607.11457, preprint).** A probabilistic data-driven *temporal*
downscaler applied to **AIFS-Single and AIFS-ENS** (and to MET Norway's Bris model). Note its stated
motivation: deterministic temporal downscaling produces **overly smooth** fields — the same defect
recurring in the time dimension. Relevant because AIFS ENS is archived at 6-hourly steps while stations
report hourly; if you want to verify at native station frequency, temporal downscaling is a prerequisite,
not an optional extra.

### 3.4 Diffusion downscaling from AIFS to km-scale

**ISTM (Niu et al. 2026, JGR Machine Learning and Computation, 10.1029/2025jh001072).** The Intelligent
Shanghai Typhoon Model: a diffusion-based downscaling emulator taking AIFS to km-scale regional fields,
reducing 72-hour typhoon intensity error by about **39.5%** relative to AIFS. Different phenomenon and
region from yours, but it establishes that AIFS → km-scale generative downscaling is a working
configuration.

### 3.5 Methodological templates from adjacent generative downscaling

- **Delefosse et al. 2026 (10.1017/eds.2026.10046)** — generative super-resolution as a post-processing
  step **decoupled from forecasting**, with a re-coarsening consistency check and spectral diagnostics.
  The cleanest methodological template in the set: decoupling means you can iterate on the downscaler
  without touching the forecast model, which is the only affordable structure on your hardware.
- **Dumont Le Brazidec et al. 2026 (arXiv 2604.03303)** — diffusion downscaling of IFS *ensembles* from
  100 km to 30 km via residual learning; **reproduces target power spectra at small scales** and preserves
  physically consistent wind–pressure coupling. Residual learning plus ensemble input is a close structural
  match to what you would build.
- **Pyrina et al. 2026 (10.1017/eds.2026.10047)** — joint bias correction and downscaling of sub-seasonal
  forecasts via diffusion. Note the *joint* framing: correcting bias and adding detail in one model rather
  than two stages.
- **AIFS vs IFS precipitation comparison (Pan et al. 2025, Weather and Forecasting,
  10.1175/waf-d-24-0227.1, 7 citations)** — AIFS-specific verification. Read it before choosing a target
  variable.

### 3.6 Station-level post-processing, which is what you are actually doing

- **STIPP (Landry et al. 2026, arXiv 2601.02882, preprint)** — the closest method template to your task.
  Space-time in-situ post-processing **at station locations** trained with proper scoring rules. Motivation
  matches your situation exactly: gridded forecasts lack precision due to unresolved local effects;
  conventional post-processing corrects bias but **degrades spatio-temporal correlation structure**; recent
  generative work fixes spatial structure but treats each lead time independently. STIPP makes joint
  spatio-temporal predictions, improving surface temperature, wind, relative humidity and precipitation,
  and produces **hourly ensembles from a six-hourly deterministic forecast** — merging post-processing with
  temporal interpolation. That is precisely the AIFS-to-station-hourly problem.
- **Vannitsem et al. 2020 (BAMS, 10.1175/bams-d-19-0308.1, 198 citations)** — the standard review of
  statistical post-processing. Read before choosing a method.
- **Rasp & Lerch 2018 (MWR, 10.1175/mwr-d-18-0187.1, 529 citations)** — distributional regression networks.
  **Implement this first.** It is simple, it is the field's reference baseline, it runs comfortably on your
  hardware, and no fancier method should be believed until it beats a properly-tuned DRN.
- **Grönquist et al. 2021 (Phil. Trans. R. Soc. A, 10.1098/rsta.2020.0092)** — deep learning for
  post-processing ensemble forecasts.
- **EUPPBench (Demaeyer et al. 2023, ESSD, 10.5194/essd-15-2635-2023, 25 citations)** — a European
  **station-based** post-processing benchmark. Structurally similar in spirit to your ISD-Lite setup; use
  it to calibrate expectations about achievable skill gains.
- **Manshausen et al. 2025 (JAMES, 10.1029/2024ms004505, 10 citations)** — generative data assimilation of
  **sparse weather station observations** at km scale, reporting **10% lower RMSE on held-out stations**.
  Note the paper's own caveat: **insufficiently dispersive ensembles**. Relevant both as method and as
  warning.
- **SEEPS4ALL (Ben-Bouallegue et al. 2026, ESSD, 10.5194/essd-18-713-2026)** — open dataset for verifying
  daily precipitation using station data. Given your empty precipitation column, this is a route to a precipitation target.
- **Rampal et al. 2024 (AIES, 10.1175/aies-d-23-0066.1, 63 citations)** — bridges the
  climate-downscaling and NWP-post-processing literatures, which use different vocabulary for similar ideas.

---

## 4. The alternative route: regional AI models instead of post-hoc downscaling

Worth understanding even if you do not take it, because one variant is a direct extension of AIFS.

### 4.1 Stretched-grid AIFS over the Nordics — the closest transferable design

**Nipen et al. 2024 (arXiv 2409.02891, preprint).** Explicitly **extends the AIFS** by introducing a
**stretched-grid architecture** that dedicates higher resolution to a region of interest while keeping
lower resolution elsewhere on the globe — feasible because GNNs naturally support arbitrary
multi-resolution grids. Applied to the Nordics at **2.5 km spatial, 6 h temporal** resolution.
**Pre-trained on 43 years of global ERA5 at 31 km, then refined on 3.3 years of 2.5 km MetCoOp Ensemble
Prediction System (MEPS) operational analyses.** It **outperforms both the control run and the ensemble
mean of MEPS for 2 m temperature.**

This is the single most geographically and methodologically transferable paper in the whole track. It is
adjacent to your domain — the Nordics border your box — and the pre-train-then-refine recipe is the pattern
that makes regional work possible without training from scratch. The honest caveat: even the *refinement*
stage here is beyond a 4 GB GPU. Read it for the design logic, not as an immediate build plan.

### 4.2 The probabilistic successor, and its one crucial finding

**Nordhagen et al. 2025 (arXiv 2511.23043, preprint).** Probabilistic stretched-grid model: 87 variables,
arbitrary ensemble size, 2.5 km over the Nordics and 31 km elsewhere, 6-hourly. Trained on a **CRPS loss
evaluated in both grid-point AND spectral space.**

**The finding you should carry into any downscaler you build:** the **spectral loss component is
*necessary* to produce spatially coherent fields** — this is *not* achieved with MSE loss, nor with CRPS in
grid-point space only. Skill numbers, verified **against surface weather stations** and compared to MEPS:
**CRPS lower by 13% for 2 m temperature and 10% for MSLP**; differences for wind speed and precipitation
were smaller.

Read §2.1 and this together. Blurring is a loss-function property. If you train a station-level downscaler
on MSE you will build the defect in; a spectral or CRPS-based objective is the documented fix.

### 4.3 The limited-area alternative and the head-to-head

- **Oskarsson et al. 2023 (Neural-LAM, arXiv 2309.17370, preprint; 7 citations on the arXiv record)** — the
  original graph-based limited-area formulation, with an open codebase. The entry point if you want to
  experiment with regional graphs.
- **Adamov et al. 2025 (arXiv 2504.09340, preprint)** — kilometre-scale ML limited-area models with a
  flexible **boundary forcing** method accepting boundaries from reanalysis *or* operational forecasts, plus
  systematic ablation of boundary width, graph construction and forcing integration. Verified against
  gridded analyses **and in-situ observations**, with a storm Ciara case study; the Swiss model beats the
  NWP baseline for key surface variables. Read for the boundary-condition engineering, which is the hard
  part of limited-area work.
- **Wijnands et al. 2025 (arXiv 2507.18378, preprint)** — direct comparison of stretched-grid vs
  limited-area for regional data-driven forecasting over Europe. Finds the stretched-grid model is
  self-contained (no external boundary conditions needed) and generalises better temporally. This is the
  paper that tells you which of the two families to pick.
- **Xu et al. 2025 (Comms. Earth & Environment, 10.1038/s43247-025-02347-5, 12 citations)** — AI-based
  limited-area model specifically for **surface** meteorological variables.
- **Bano-Medina et al. 2025 (npj Clim. Atmos. Sci., 10.1038/s41612-025-01265-9)** — regional stretched-grid
  AI model at 6 km over the western US, capturing extreme precipitation that coarse global models
  underestimate.

**Assessment against your constraints.** The regional-model route needs multi-GPU training and, in the
Nordic case, a high-resolution regional analysis (MEPS) for refinement. You have neither: 4 GB VRAM, and no
km-scale gridded analysis for NW Russia in the open-data domain. **Post-hoc station-level post-processing
of AIFS is the route your hardware and data actually support** — which is also the route with a direct
operational precedent (§3.1). Read §4 to steal the loss-function lesson, not the training pipeline.

---

## 5. Gaps a NW-Russia AIFS downscaling project could occupy

Ordered by how defensible each gap is, given what the searches actually returned.

1. **No AI-model verification or downscaling study anywhere in NW Russia / European high-latitude Russia.**
   Targeted searches for Arctic, Nordic, Baltic, Barents and Russia-specific AI-model verification returned
   nothing on-topic. The nearest work stops at the Nordic border (§4.1–4.2). Combined with Olivetti &
   Messori's finding that data-driven skill on extremes **varies by region and is best nearer the tropics**
   (10.5194/gmd-17-7915-2024), the assumption that published global skill transfers to 55–70.5 °N is
   **untested**. This is the cleanest gap: a station-based AIFS verification over your 144 stations would be
   a genuine contribution before any downscaling at all.

2. **No study isolating AI-model error in the stable boundary layer or under snow cover.** These two
   regimes dominate winter 2 m temperature error at your latitudes. Searches on snow/boreal/stable-boundary-
   layer AI-model bias returned only land-surface emulation (10.5194/gmd-18-921-2025) and classical
   downscaling (10.1175/jamc-d-20-0057.1), nothing on AI forecast models specifically. Strong seasonal
   stratification of your verification would speak directly into this.

3. **The stale-climatology cold bias has not been tested on AIFS.** Landsberg et al.
   (10.1029/2025gl119740) document a 15–20 year climatological lag in FourCastNet and Pangu, concentrated in
   the hottest temperatures, in **boreal winter over land** — your exact regime. AIFS was not among the
   models tested. Whether an operationally-retrained model inherits the same lag is open, and answerable
   with station data.

4. **AIFS downscaling work to date targets precipitation and typhoons, not near-surface temperature over
   a station network.** SwAIther-Precip is precipitation over Switzerland (arXiv 2605.16163); ISTM is
   typhoon intensity (10.1029/2025jh001072); HourGlass is temporal rather than spatial (arXiv 2607.11457).
   Trotta et al. is the closest in spirit but applies an existing operational system in Australia
   (10.1175/aies-d-25-0037.1). **Station-level spatial downscaling of AIFS ENS 2 m temperature in a boreal
   domain is unoccupied.** Your data supports exactly this (temperature/dew point/wind ~99–100% complete).

5. **Downscaling under a representativeness-error budget is under-treated.** You have measured what most
   papers do not: station-minus-model orography spanning −128 to +72 m (σ = 29 m), and 15 of 144 stations on
   cells the model calls water. The complex-terrain downscaling literature (10.1175/jamc-d-20-0057.1) treats
   elevation as a predictor, but framing an irreducible-error floor from measured representativeness
   mismatch — and then asking how much of the remaining error a downscaler can actually remove — would be a
   methodological contribution, not just a regional application.

6. **The ensemble-member vs ensemble-mean choice is stated but not systematically tested for
   station-level downscaling.** Mahesh et al. (10.5194/gmd-18-5575-2025) show members retain spectra while
   the mean degrades; no paper I retrieved compares downscaling members against downscaling the mean at
   station level with proper scores. This is a cheap, well-posed experiment on your hardware.

7. **AIFS-DOP (arXiv 2606.19093) has no independent evaluation yet.** An observation-trained model
   sidesteps your central verification problem — that ERA5 assimilates the SYNOP stations you validate
   against. Nobody has evaluated it against an independent station network.

---

## 6. Annotated reading order

**Tier 1 — read before writing any code (4 papers).**

1. **Trotta et al. 2025, AIES, 10.1175/aies-d-25-0037.1** — your project already has an operational
   precedent; existing post-processing methods transfer to AIFS unmodified, and blending beats picking.
2. **Lang et al. 2024, arXiv 2406.01465** + **Moldovan et al. 2025, arXiv 2509.18994** — what AIFS is, and
   which version you are downloading. Count as one reading.
3. **Bonavita 2024, GRL, 10.1029/2023gl107377** — the defect you are trying to fix, stated canonically,
   including why RMSE rewards blurring.
4. **Gabler et al. 2026, arXiv 2608.09972** — station-based extremes verification across 11 systems, with
   AIFS's quantified heat-tail penalty and the shared centre-of-distribution bias. The closest existing
   work to your evaluation design.

**Tier 2 — method selection (5 papers).**

5. **Rasp & Lerch 2018, MWR, 10.1175/mwr-d-18-0187.1** — build this baseline first.
6. **Vannitsem et al. 2020, BAMS, 10.1175/bams-d-19-0308.1** — the method landscape before you commit.
7. **Nordhagen et al. 2025, arXiv 2511.23043** — the spectral-loss lesson: MSE will bake in the blur.
8. **Landry et al. 2026 (STIPP), arXiv 2601.02882** — station-located, proper-scoring-rule post-processing;
   6-hourly deterministic in, hourly ensemble out.
9. **Assouline et al. 2026 (SwAIther-Precip), arXiv 2605.16163** — the closest analogue to your idea, with
   the lead-time-aware-training lesson and an honest effective-resolution number.

**Tier 3 — evaluation design and context (5 papers).**

10. **Rasp et al. 2024, WeatherBench 2, JAMES, 10.1029/2023ms004019** — metric definitions so your numbers are
    comparable.
11. **Ben Bouallègue et al. 2024, BAMS, 10.1175/bams-d-23-0162.1** — how these models behave in operations.
12. **Olivetti & Messori 2024, GMD, 10.5194/gmd-17-7915-2024** — why regional skill cannot be assumed from
    global scores.
13. **Nipen et al. 2024, arXiv 2409.02891** — the Nordic stretched-grid AIFS extension; the road not taken,
    and why.
14. **Landsberg et al. 2026, GRL, 10.1029/2025gl119740** — the stale-climatology cold bias your training
    archive could inherit.

**Tier 4 — as needed.** Mahesh et al. (10.5194/gmd-18-5575-2025) on members vs mean; Brenowitz et al.
(10.1029/2024gl113656) on effective resolution and dispersion; Rodwell et al. (10.1002/met.70071) for
spectral diagnostics; Wesselkamp et al. (10.5194/gmd-18-921-2025) for land-surface model classes that fit
your hardware; Demaeyer et al. (10.5194/essd-15-2635-2023) for benchmark skill expectations; Wijnands et al.
(arXiv 2507.18378) if you reconsider the regional-model route.

---

## 7. Coverage caveats — where this review is weak

- **Preprints are 26 of 63 references.** This field moves faster than peer review; the AIFS-specific
  downscaling work (SwAIther-Precip, HourGlass) and both Nordic stretched-grid papers are preprints and are
  flagged as such in the CSV. Treat their numbers as provisional.
- **Some quantitative detail comes from preprint abstracts** because OpenAlex carries no abstract for
  several AMS and Nature-family journal records. Where a journal and preprint version both exist, the CSV
  gives the journal record; the numbers quoted are traceable to the abstract of one or the other. I did not
  read full texts except for Trotta et al.
- **Citation counts are OpenAlex counts at retrieval time** and are missing for arXiv-only records.
  Recent papers are structurally undercounted — Gabler et al. and SwAIther-Precip matter more to you than
  their (absent) counts suggest.
- **Genuinely thin areas, searched and confirmed thin:** high-latitude/Arctic AI-model verification;
  stable-boundary-layer and snow-cover behaviour of AI models; any Russia-specific work. These returned
  empty or off-topic results across multiple query formulations. I am reporting absence, not asserting it
  as proven non-existence — but the absence was consistent.
- **Not covered by design:** the pure climate-emulation literature (except where it bears on the stale-
  climatology bias), nowcasting, and non-ECMWF operational AI systems beyond the comparison set.
