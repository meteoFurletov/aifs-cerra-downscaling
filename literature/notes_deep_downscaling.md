# Deep-learning downscaling of atmospheric fields: what the literature actually supports

**Scope of this track.** Grid-to-grid super-resolution (CNN/U-Net, GAN, diffusion), the
perfect-prognosis versus MOS framing question, and generative/stochastic methods that produce
calibrated fine-scale variability. 71 papers retrieved and verified (16 preprints, clearly labelled
as such). Written for a project whose target is AIFS ENS forecasts over northwest Russia, with
station observations as the only available truth and a single 4 GB GPU as the only accelerator.

Two things dominate the honest reading of this literature, and they are worth stating before the
detail:

1. **Almost the entire DL downscaling literature is trained and validated in a setting that does
   not match the project's setting.** The overwhelming majority of papers map *reanalysis* to
   *a high-resolution model's own output* — ERA5 to COSMO-CLM, ERA5 to CONUS404, 25 km reanalysis
   to a 2 km regional model. The truth field is a numerical simulation, not an observation. The
   input is an analysis, not a forecast. Both substitutions inflate reported skill relative to what
   the same method delivers on live forecasts verified at stations.
2. **The field knows this, but states it in fragments rather than in one canonical paper.** There is
   no single well-cited paper that makes the assimilation-circularity argument formally in the form
   this project needs. There are four partial statements, and together they are enough to build the
   argument — see §2.

---

## 1. Grid-to-grid super-resolution: three families

### 1.1 CNN and U-Net (deterministic)

The lineage starts with stacked SRCNN applied to climate fields (DeepSD,
doi:10.1145/3097983.3098004) and matures into the two papers that established how such a model
should be *validated*: Baño-Medina et al. (2020, doi:10.5194/gmd-13-2109-2020) intercompared CNNs
of increasing complexity against linear and generalized-linear benchmarks for temperature and
precipitation over Europe, deliberately inside the VALUE validation framework and deliberately
using large-scale "perfect" reanalysis predictors. Their motivation is explicitly epistemic — that
existing studies used "complex models, applied to particular case studies and using simple
validation frameworks", so that the added value of DL could not be assessed. Read the companion
paper next (doi:10.1007/s00382-021-05847-0): it takes the *same* CNNs from reanalysis predictors to
GCM predictors and analyses the two key assumptions that this substitution requires. That pair is
the methodological backbone of the deterministic branch.

For the variables this project actually has (temperature, dew point, wind — not precipitation), the
relevant deterministic work is:

- **Temperature.** Sha et al. (2020, doi:10.1175/jamc-d-20-0057.1) — U-Net gridded downscaling of
  daily maximum and minimum 2-m temperature in complex terrain; Part II covers daily precipitation
  (doi:10.1175/jamc-d-20-0058.1). These are among the few grid-to-grid DL papers where temperature,
  not rainfall, is the headline variable.
- **Wind.** Höhlein et al. (2020, doi:10.1002/met.1961) is the single closest architectural template
  in this entire track. They downscale *short-range forecasts* of 100-m wind from ERA5 at 31 km to
  mimic HRES at 9 km, compare four CNN architectures against multilinear regression, propose a
  U-Net variant (DeepRU), and — importantly for a project with 144 stations sitting on badly
  represented orography — test whether adding static high-resolution fields (topography, land–sea
  mask, forecast surface roughness) and extra atmospheric predictors such as geopotential height
  improves skill. The resolution jump (31 km → 9 km) is modest, which is exactly the regime a
  0.25° AIFS input sits in.
- **Multi-variable production pipelines.** Lin et al. (2023, doi:10.1038/s41597-023-02805-9) built a
  nine-variable 0.1° dataset over East Asia by bias-correcting then U-Net-downscaling CMIP6 against
  MSWX; Soares et al. (2024, doi:10.5194/gmd-17-229-2024) compared four CNN architectures
  downscaling seven CMIP6 models to 0.1° over Iberia. Both are useful as evidence on architecture
  choice at regional scale; neither is forecast-applied.

The **RCM-emulator** framing (Doury et al. 2022, doi:10.1007/s00382-022-06343-9) is worth
understanding as a distinct idea: instead of learning observation statistics, the network learns the
regional model's *own* downscaling function, so that cheap ensemble members can be generated. It is
the cleanest formulation of "what a downscaler is a function of", and it sets up §2.

### 1.2 GANs

Leinonen et al. (2020, doi:10.1109/tgrs.2020.3032790) introduced recurrent *stochastic*
super-resolution — a conditional GAN generating ensembles of time-evolving high-resolution fields,
tested on Swiss radar precipitation and GOES-16 cloud optical thickness, with the ensemble's
statistical properties assessed using rank statistics. Their framing matters: conditional GANs
naturally generate an ensemble of solutions for one input, and the atmospheric-science use case
needs that, whereas computer-vision super-resolution usually ignores it.

Harris et al. (2022, doi:10.1029/2022ms003120) is the paper to read after it, because it makes the
jump this project needs: from reconstructing artificially coarsened fields to *increasing the
accuracy and resolution of genuinely low-resolution weather-model output*, with high-resolution
radar as truth. Their framing of why precipitation is the hard case — key processes occur below the
resolved scale of global models — applies directly. Price & Rasp (2022, arXiv:2203.12297, preprint;
see also arXiv:2210.12504) push the same idea to global ensemble forecasts over CONUS with
CorrectorGAN, simultaneously correcting and super-resolving, again with radar as ground truth.

Elsewhere in the GAN branch: adversarial super-resolution of climatological wind and solar fields
(doi:10.1073/pnas.1918964117); physically constrained GANs for ESM precipitation
(doi:10.1038/s42256-022-00540-1); wind-field downscaling over Switzerland
(doi:10.1175/aies-d-22-0018.1); and a design aimed explicitly at *reliability* rather than sharpness
alone (doi:10.1029/2024ms004668). RainScaleGAN (doi:10.1175/aies-d-24-0074.1) and a
quantile-regression ensemble (doi:10.1609/aaai.v38i20.30193) round out the precipitation-tail work,
the latter being a notably cheaper route to tail calibration than adversarial training.

### 1.3 Diffusion

**CorrDiff** (Mardani et al. 2025, doi:10.1038/s43247-025-02042-5; preprint arXiv:2309.15214) is the
reference architecture, and its two-step structure is the single most transferable design idea in
this track: a U-Net predicts the conditional *mean*, and a corrector diffusion model predicts the
*residual*. It maps 25 km global reanalysis to 2 km regional-model output over Taiwan, predicts
channels beyond those present in the input, and — the key result — recovers the power-law spectral
relationships of the target that deterministic regression destroys, in addition to competitive bulk
MAE and CRPS.

For this project's variables, the closest diffusion paper is Tomasi et al. (2025,
doi:10.5194/gmd-18-2051-2025): a latent diffusion model downscaling ERA5 to 2 km over Italy for
**2-m temperature and 10-m horizontal wind components**, targeting a COSMO-CLM dynamical
downscaling, built as a residual on top of a U-Net reference. It is the temperature-and-wind
analogue of CorrDiff and is explicit that the goal is to match a dynamical model given the same
inputs.

Other diffusion work worth knowing: spatiotemporal video diffusion for precipitation
(arXiv:2312.06071, preprint) whose framing — that the application needs the accurate *conditional
distribution*, not a good mean, to get reliable ensemble averages and unbiased extremes — is the
clearest statement of the generative rationale; TAUDiff (arXiv:2412.13627, preprint), which names
spectral bias in deterministic regression as the problem and pairs a deterministic mean-field model
with a *smaller* generative model for the fine-scale residual; joint bias-correction-and-downscaling
by conditional diffusion trained on observations only via a shared embedding space
(doi:10.5194/gmd-19-1791-2026); dynamical-generative hybrid downscaling
(doi:10.1073/pnas.2420288122); global spatio-temporal generative downscaling of ERA5 precipitation
from 24 km/1 h to 2 km/10 min (spateGAN-ERA5, doi:10.1038/s41612-025-01103-y); and a wavelet-domain
conditional diffusion reporting 10× super-resolution to 1 km with a 9× inference speed-up over
pixel-space diffusion (doi:10.1029/2025jh000941).

### 1.4 Which of these were applied to forecasts?

This is the discriminating question, and the answer is: **a small minority.**

Forecast-applied (MOS framing): Höhlein et al. 2020 (ERA5-initialised short-range wind forecasts →
HRES); Harris et al. 2022 and Price & Rasp 2022 (weather-model precipitation → radar);
SwAIther-Precip (arXiv:2605.16163, preprint — AIFS → km-scale over Switzerland); ACDF
(arXiv:2603.12828, preprint — Pangu → 500 m winds); probabilistic bias correction of AIFS and IFS
at subseasonal range (arXiv:2604.16238, preprint).

Reanalysis- or model-applied (perfect-prognosis or emulator framing): essentially everything else in
§1.1–1.3, including CorrDiff, Tomasi, spateGAN-ERA5, DeepSD, Baño-Medina, Sha, Soares, Lin, Doury,
Stengel, Miralles, Rampal.

---

## 2. The framing question: perfect prognosis versus MOS

### 2.1 The taxonomy, and where the "perfect" assumption enters

The PP / MOS / weather-generator taxonomy comes from the precipitation-downscaling review of Maraun
et al. (2010, doi:10.1029/2009rg000314). The distinction that matters here is:

- **Perfect prognosis (PP):** learn a mapping from *large-scale predictors taken from reanalysis* to
  local observations, then apply that mapping to model output. The word "perfect" is not a
  compliment — it labels the assumption that the predictors you will eventually feed the model are
  as good as the reanalysis ones you trained on.
- **MOS:** learn a mapping from *the actual model's output* (with its actual biases, at its actual
  resolution, at a given lead time) to observations.

The VALUE project made this operational. Gutiérrez et al. (2018, doi:10.1002/joc.5462) ran the
largest controlled intercomparison to date — over 50 methods across all three families, 86 European
stations — and did so under *deliberately* "perfect" reanalysis-driven predictors, precisely so that
the intrinsic performance of the methods could be separated from driving-model error. The synthesis
paper (Maraun et al. 2018, doi:10.1002/joc.5877) reports the results that bear directly on this
project:

- MOS "performs mostly well, but requires predictors at a resolution close to the target one" — i.e.
  the MOS framing is not resolution-agnostic;
- PP performance "depends crucially on model structure and predictor choice";
- **inter-annual variability is under-represented by both PP methods and weather generators**;
- **spatial variability is poorly represented by almost all participating methods** — MOS inherits
  it from the driving model, and PP and weather-generator methods do not represent it at all.

That last pair of findings is the variance problem of §3 appearing in the pre-deep-learning
literature, measured across 50+ methods.

### 2.2 The formal statements that skill does not transfer

I searched hard for a paper that says "downscaling skill measured against a reanalysis that
assimilated your verification stations is circular." **No single canonical paper makes that argument
in that form.** What exists instead are four rigorous partial statements, and stacking them gives
the argument:

**(a) The perfect-versus-imperfect training-framework experiment.** Van der Meer et al. (2023,
doi:10.1029/2022ms003593) is the closest thing to a controlled demonstration, and it should be read
in full. They train the same RCM-emulator twice: once in a **perfect model framework** (predictors
are upscaled RCM fields, so the emulator learns *only* the downscaling function) and once in an
**imperfect model framework** (predictors are actual GCM fields, so the emulator is exposed to
GCM–RCM inconsistency during training). The perfect-framework emulator "accurately reproduced" the
target when evaluated on upscaled data — and then, when applied to real GCM data, "conserved
RCM-GCM inconsistencies and led to underestimation." That is the transfer failure, isolated
experimentally, with the training framework as the only manipulated variable. Substitute
"reanalysis" for "upscaled RCM" and "AIFS forecast" for "GCM" and it is this project's situation.

**(b) The assumptions behind PP, tested explicitly.** Baño-Medina et al. (2021,
doi:10.1007/s00382-021-05847-0) take CNNs validated under perfect reanalysis predictors and analyse
the two key assumptions required to apply them to GCM predictors, motivated by the risk of
"uncontrolled extrapolation artifacts" from black-box models. Gutiérrez et al. (2012,
doi:10.1175/jcli-d-11-00687.1) is the pre-DL version of the same concern.

**(c) Held-out scores can be uninformative by construction.** Maraun & Widmann (2018,
doi:10.5194/hess-22-4867-2018) show analytically that cross-validating bias-corrected free-running
simulations against observations is *misleading*: the residual bias in the validation period depends
solely on the difference between simulated and observed change across calibration and validation
periods, which is itself dominated by internal variability. The general lesson — that a held-out
score can be governed by something other than the quality of the correction — is why this project's
own ERA5 result (no method beat raw ERA5 on held-out data) should be read as informative about the
*setup*, not only about the methods.

**(d) Standard validation is insufficient for DL specifically.** González-Abad et al. (2023,
doi:10.1029/2023ms003641) intercompare PP-approach DL downscaling models on one use case and argue
that standard evaluation must be extended, introducing saliency-based diagnostics (Aggregated
Saliency Map, Saliency Dispersion Maps) to expose what the network is actually keying on. If two
models score the same and attend to different predictors, the held-out RMSE was not measuring what
you thought.

Two older references complete the reading list on reanalysis-as-predictor, and I flag a limitation:
Brands et al. (2011, doi:10.1175/jcli-d-11-00251.1, "On the Use of Reanalysis Data for Downscaling")
and Eden et al. (2012, doi:10.1175/jcli-d-11-00254.1, "Skill, Correction, and Downscaling of
GCM-Simulated Precipitation") are both directly on topic and well cited (109 and 201 citations), but
**their abstracts were not retrievable through the search API, so I am citing them at title level
only** — verify their content yourself before leaning on them.

### 2.3 The MOS-framing literature is a different body of work

An important practical point that the downscaling literature obscures: the methods that actually
work on live forecasts verified at stations mostly live in the **statistical postprocessing**
literature, not the downscaling literature. Start from the community review (Vannitsem et al. 2020,
doi:10.1175/bams-d-19-0308.1), then:

- **Rasp & Lerch (2018, doi:10.1175/mwr-d-18-0187.1)** — the most directly usable paper in this
  entire track. Neural-network distributional regression postprocessing of 2-m temperature at German
  surface *stations*, learning predictive-distribution parameters instead of pre-specified link
  functions, using auxiliary predictors and **station-specific embeddings**. It significantly
  outperforms benchmark postprocessing methods "while being computationally more affordable". 529
  citations. The station-embedding trick is the natural way to handle 144 stations with
  station-specific representativeness errors.
- **Schulz & Lerch (2021, doi:10.1175/mwr-d-21-0150.1)** — a systematic comparison of eight methods
  for wind gusts spanning three groups: classical (EMOS, member-by-member, isotonic distributional
  regression), established ML (gradient-boosted EMOS, quantile regression forests), and
  neural-network (distributional regression network, Bernstein quantile network, histogram estimation
  network). This is the benchmark ladder to climb before touching anything generative.
- **Höhlein et al. (2023, doi:10.1175/aies-d-23-0070.1)** — permutation-invariant networks that
  consume the ensemble as an unordered *set* of members rather than as summary statistics, for
  temperature and wind gusts. For 51 exchangeable AIFS-ENS members this is the architecturally
  correct choice, and it is not widely known outside the postprocessing community.

---

## 3. Generative and stochastic approaches, and the variance argument

### 3.1 Why MSE-trained deterministic super-resolution under-represents fine-scale variance

The argument exists in three distinct forms, and it is worth holding all three.

**The statistical form (oldest, strongest).** Maraun (2013, doi:10.1175/jcli-d-12-00821.1),
"Bias Correction, Quantile Mapping, and Downscaling: Revisiting the Inflation Issue", 771 citations,
is the theoretical root. A regression that minimises squared error is a *conditional mean*
estimator; the conditional mean of a fine-scale field has less variance than the field itself. You
cannot fix this by inflating the variance without corrupting the deterministic part of the signal —
inflation and randomisation are not interchangeable, and treating them as such is the classic error.
Any DL paper claiming to have discovered "spectral bias" is rediscovering this result with a
different vocabulary. Stochastic MOS (Wong et al. 2014, doi:10.1175/jcli-d-13-00604.1) is the
pre-DL constructive answer.

**The forecast-verification form.** MSE-optimal forecasts are smooth because of the double penalty:
a sharp field placed slightly wrong is penalised twice, so the loss-minimising output hedges toward
the mean. Subich et al. (arXiv:2501.19374, preprint) quantify this for data-driven weather models
and, crucially, *fix it cheaply*: a parameter-free modification separating decorrelation loss from
spectral-amplitude loss, applied by **fine-tuning** GraphCast, raised the model's effective
resolution from 1250 km to 160 km while also improving ensemble spread and surface wind extremes.
This is the clearest published quantification of MSE-induced smoothing anywhere in the corpus, and
the intervention is at fine-tuning scale rather than training-from-scratch scale.

**The generative-model form.** Ravuri et al. (2021, doi:10.1038/s41586-021-03854-z) state the
failure mode plainly for radar nowcasting: methods without constraints "produce blurry nowcasts at
longer lead times, yielding poor performance on rarer medium-to-heavy rain events". The
video-diffusion paper (arXiv:2312.06071, preprint) generalises the requirement — the application
needs the correct conditional *distribution* to get reliable ensemble means and unbiased extremes.

**The strongest single number** for "generative beats MSE on the tails" is Rampal et al. (2024,
doi:10.1029/2024gl112492): for 99.5th-percentile daily precipitation, against an RCM projecting a
robust ~5.8 %/°C end-of-century increase, a GAN trained on a future climate captured **97 %** of the
warming-driven increase versus **65 %** for the deterministic CNN baseline; a GAN trained only on
historical data still captured **77 %**. Same backbone, adversarial versus deterministic training —
the gap is the variance deficit, quantified.

### 3.2 Diagnostics: how to tell real variability from cosmetic sharpness

This is where the recent literature has become genuinely useful, and it is what would make a
NW-Russia study credible.

- **Spectra.** CorrDiff's headline evidence is spectral, not RMSE-based
  (doi:10.1038/s43247-025-02042-5). Rodwell et al. (2025, doi:10.1002/met.70071) provide the
  reference frame: power spectra of ECMWF physics-based *and* data-driven ensembles, charting where
  spread and error diverge by scale, with extratropical small-scale variance saturating quickly while
  planetary-scale error remains unsaturated at day 10, and over-dispersion at synoptic scales at
  intermediate lead times. This is the diagnostic vocabulary to adopt.
- **Physical consistency.** Kim et al. (2026, doi:10.1038/s41612-026-01380-1) apply a spectral test
  of error growth and physical consistency to GenCast ensembles — the right way to ask whether
  generated fine-scale structure is physically meaningful rather than decorative.
- **Derived fields.** Saccardi et al. (arXiv:2510.13722, preprint) benchmark generative downscalers
  with physics-inspired diagnostics and find that models scoring well on standard ML metrics fail on
  second-order derived quantities such as divergence and vorticity.
- **Probabilistic scoring done properly.** Brenowitz et al. (2025, doi:10.1029/2024gl113656) show via
  lagged initial-condition ensembles that models can rank differently on probabilistic skill than on
  deterministic skill: GraphCast and Pangu lagged ensembles perform similarly even though GraphCast
  wins deterministically. Deterministic RMSE is not a proxy for ensemble skill.

### 3.3 Compute cost: what is and is not reachable on one 4 GB GPU

Ordered from clearly feasible to clearly out of reach.

**Feasible.**
- Station-level distributional-regression networks and their ML competitors (Rasp & Lerch 2018;
  Schulz & Lerch 2021; Höhlein et al. 2023). These are small networks over tabular
  predictors-at-stations. This is the right first project.
- Modest-jump deterministic CNN/U-Net grid-to-grid mapping over a regional box (Höhlein et al. 2020;
  Sha et al. 2020). A 0.25° → ~2–5 km U-Net over a 15°×20° box is trainable on 4 GB with patch-based
  training and mixed precision, though patch size will be the binding constraint.
- The two-stage *correct-then-refine* pattern where only the cheap stage is generative — the design
  logic of SwAIther-Precip (arXiv:2605.16163, preprint) and TAUDiff (arXiv:2412.13627, preprint).
  SwAIther's key economy is that conditioning the super-resolution stage only on corrected
  precipitation (rather than on the full atmospheric state) allows **direct training on
  observations** — the exact situation of a project whose only truth is station data.
- Evidence that the whole pipeline fits on modest hardware: ACDF (arXiv:2603.12828, preprint)
  produces 500 m wind fields over a province-scale domain in roughly 25 s per 12-h cycle **on a
  single GPU**, and reports a 38.8 % reduction in station-scale wind-speed MAE relative to
  Pangu-Weather.
- Fine-tuning or regionally adapting an existing model rather than training one (arXiv:2409.07585,
  preprint, for the MENA region; arXiv:2501.19374, preprint, for the loss-function fix). Note the
  4 GB ceiling still bites for fine-tuning a global model — the MENA-style regional adaptation is the
  more realistic version.
- CRPS-trained single-pass ensemble generation instead of diffusion sampling. CRPS-LAM
  (arXiv:2510.09484, preprint) reports roughly **39× speed-up over diffusion baselines** by
  generating members in one forward pass, using a hybrid CNN/GNN backbone.

**Marginal.** Conditional GANs at modest patch size (Leinonen et al. 2020; Harris et al. 2022) —
trainable but adversarial training is unstable and the debugging cost on limited hardware is real.
Prefer the quantile-regression route to tail calibration (doi:10.1609/aaai.v38i20.30193) or
reliability-oriented GAN designs (doi:10.1029/2024ms004668) if attempting this.

**Out of reach.** Training a diffusion downscaler from scratch at CorrDiff scale
(doi:10.1038/s43247-025-02042-5); latent diffusion over a large domain
(doi:10.5194/gmd-18-2051-2025) — cheaper than pixel-space but still not a 4 GB proposition for
training; AI limited-area emulators trained on 40 years of hourly km-scale target data
(arXiv:2602.18646, preprint); huge SFNO ensembles (doi:10.5194/gmd-18-5575-2025); anything requiring
a km-scale dynamical dataset as the training target, since northwest Russia has no open equivalent
of CONUS404 or a national COSMO-CLM archive. Wavelet-domain diffusion
(doi:10.1029/2025jh000941) reduces *inference* cost 9×, which does not solve the training problem.

### 3.4 What the AIFS input actually is

Read the AIFS ensemble paper before designing anything: Lang et al. (2026,
doi:10.1038/s44387-026-00073-7; preprint arXiv:2412.15832) describe AIFS-CRPS, trained with the
almost-fair CRPS, stochastic, able to generate arbitrarily many exchangeable members, and
outperforming the IFS ensemble for the majority of variables and lead times in the medium range.
Two consequences: (i) the members are *exchangeable*, which is what makes permutation-invariant
postprocessing appropriate; (ii) a CRPS-trained ensemble is already calibration-aware, so a
postprocessing step that assumes raw-ensemble underdispersion may find less to fix than the IFS-era
literature implies. Also check which AIFS version an archive corresponds to — the update in
arXiv:2509.18994 (preprint) added physical-consistency bounding layers that substantially improved
precipitation and has been operational since 25 February 2025. Baseline expectations for AI-model
skill in an operational-like setting come from Ben Bouallègue et al. (2024,
doi:10.1175/bams-d-23-0162.1); for a high-impact European windstorm case, Charlton-Perez et al.
(2024, doi:10.1038/s41612-024-00638-w) found four ML models captured the synoptic-scale cyclone
structure well. GenCast (Price et al. 2024, doi:10.1038/s41586-024-08252-9) is the reference for
diffusion-based global ensembles.

---

## 4. What this means for a NW-Russia AIFS downscaling project

**The project's own ERA5 result is not an anomaly — it is the literature's central warning, observed
first-hand.** No method beating raw ERA5 toward stations that ERA5 assimilates is exactly what van
der Meer et al.'s perfect-framework emulator did when moved to real driving data
(doi:10.1029/2022ms003593), and exactly what the VALUE synthesis predicts when the driving field is
"perfect" (doi:10.1002/joc.5877). The correct inference — downscale forecasts, not analyses — is the
inference the literature supports. Nothing found here contradicts it.

**The realistic first project is station-level probabilistic postprocessing of AIFS ENS, not
grid-to-grid super-resolution.** Rasp & Lerch's architecture with station embeddings
(doi:10.1175/mwr-d-18-0187.1), benchmarked against the Schulz & Lerch ladder
(doi:10.1175/mwr-d-21-0150.1), consuming members permutation-invariantly
(doi:10.1175/aies-d-23-0070.1), on temperature, dew point and wind — the three variables that are
99–100 % complete in the station archive. This is defensible, publishable, hardware-feasible, and
avoids the precipitation gap entirely. Station embeddings are also the natural mechanism for
absorbing the −128 to +72 m elevation mismatch and the 15 stations sitting on cells the model calls
water: let the network learn a per-station correction rather than imposing a lapse rate.

**If grid-to-grid is attempted, the honest framing is a two-stage correct-then-refine pipeline
trained on stations.** SwAIther-Precip (arXiv:2605.16163, preprint) is the template: lead-time-aware
bias correction at coarse resolution first — lead-time conditioning matters because forecast bias is
lead-time-dependent in a way reanalysis bias is not — then a cheap refinement stage conditioned only
on the corrected field, trained directly on observations. ACDF (arXiv:2603.12828, preprint)
demonstrates the same correct-then-downscale separation for wind on a single GPU. Höhlein et al.
(doi:10.1002/met.1961) supplies the architecture and the static-predictor set.

**Do not import a pretrained generative downscaler.** Saccardi et al. (arXiv:2510.13722, preprint)
found CorrDiff-class models trained on central Europe failed to generalise to Iberia, Morocco **and
Scandinavia** — the last being the nearest analogue region to this domain — and failed on derived
divergence and vorticity. spateGAN-ERA5 (doi:10.1038/s41612-025-01103-y) trained only on Germany and
validated elsewhere is the optimistic counterpoint, and a systematic 15-region transferability study
exists (arXiv:2512.01400, preprint), but the burden of proof is on transfer, not against it. A
high-latitude domain with a long snow season, a large Baltic/White Sea land–water contrast and
weak orography is not central Europe.

**The gap this project could occupy is real and specific.** See §5.

---

## 5. Gaps found

1. **No canonical paper on assimilation circularity in downscaling evaluation.** The argument that
   verifying a reanalysis-trained downscaler against stations the reanalysis assimilated is circular
   exists only implicitly — in VALUE's "perfect predictor" construction (doi:10.1002/joc.5462), in
   the perfect-versus-imperfect emulator experiment (doi:10.1029/2022ms003593), and in the
   cross-validation critique (doi:10.5194/hess-22-4867-2018). A paper stating it directly, with a
   worked example at stations, appears not to exist. This project has already produced the empirical
   result that would anchor such a paper.
2. **Almost no forecast-applied DL downscaling verified at stations, and almost none for
   temperature or wind.** The forecast-applied set is small and precipitation-dominated
   (doi:10.1029/2022ms003120; arXiv:2203.12297; arXiv:2605.16163), with radar rather than stations
   as truth. Höhlein et al. (doi:10.1002/met.1961) is forecast-applied for wind but verifies against
   *HRES*, i.e. model against model.
3. **High latitudes are essentially absent.** The only northern-European statistical downscaling
   paper retrieved was Benestad et al. (2025, doi:10.5194/hess-29-45-2025) on heavy-rainfall
   probability over the Nordic countries — empirical-statistical, not DL, and precipitation-focused.
   Searches aimed specifically at Russian/Arctic downscaling returned nothing usable. Snow-season
   surface coupling, strong stable boundary layers, and land–sea-ice contrast are all conditions
   under which a mid-latitude-trained downscaler has no evidence base.
4. **No open km-scale dynamical training target for this domain.** The dominant DL downscaling
   recipe needs a high-resolution model archive as truth (CONUS404, COSMO-CLM, a 2 km regional
   model). Northwest Russia has no open equivalent, which structurally forces observation-trained
   methods — a constraint the literature rarely confronts, and which the SwAIther design
   (arXiv:2605.16163) and the observation-only diffusion approach (doi:10.5194/gmd-19-1791-2026)
   address most directly.
5. **Postprocessing of a CRPS-trained AI ensemble is largely unexplored.** The station-postprocessing
   benchmarks were built on IFS-era ensembles. Whether the classic corrections still add value on top
   of AIFS-CRPS (doi:10.1038/s44387-026-00073-7), which is already trained on a proper score, is an
   open and cheaply answerable question. arXiv:2604.16238 (preprint) reports large gains at
   subseasonal range, which does not settle the medium-range station-level case.
6. **Variance diagnostics are not standard in station-level work.** The spectral and physical-
   consistency diagnostics of §3.2 are grid-based. There is no established equivalent for verifying
   that a station-level probabilistic downscaler reproduces temporal variance and extremes, beyond
   CRPS and rank histograms — and the VALUE synthesis already flagged inter-annual variability as
   under-represented across method families (doi:10.1002/joc.5877).

---

## 6. Annotated reading order

1. **Maraun et al. 2018, doi:10.1002/joc.5877** — VALUE synthesis. Read first; it defines the
   framing question and reports the variance findings.
2. **van der Meer et al. 2023, doi:10.1029/2022ms003593** — the perfect-versus-imperfect training
   framework experiment. The transfer failure, isolated.
3. **Rasp & Lerch 2018, doi:10.1175/mwr-d-18-0187.1** — the method to implement first.
4. **Maraun 2013, doi:10.1175/jcli-d-12-00821.1** — the inflation issue; why MSE training loses
   variance and why naive fixes fail.
5. **Mardani et al. 2025, doi:10.1038/s43247-025-02042-5** — CorrDiff; the mean-plus-residual
   architecture and spectral evidence.
6. **arXiv:2605.16163 (preprint)** — SwAIther-Precip; the AIFS-specific, observation-trained,
   lead-time-aware pipeline. Closest existing work to the project.
7. **Höhlein et al. 2020, doi:10.1002/met.1961** — architecture and static predictors for
   forecast wind downscaling at a modest resolution jump.
8. **arXiv:2510.13722 (preprint)** — the generalisation failure, including to Scandinavia. Read
   before considering any pretrained model.
9. **Schulz & Lerch 2021, doi:10.1175/mwr-d-21-0150.1** and **Höhlein et al. 2023,
   doi:10.1175/aies-d-23-0070.1** — the benchmark ladder and the set-based architecture.
10. **Lang et al. 2026, doi:10.1038/s44387-026-00073-7** — what AIFS ENS actually is.

---

## 7. What I searched, and where the literature was thin

**Searched (OpenAlex and arXiv, ~45 distinct queries across seven rounds, plus forward-citation and
backward-reference walks on six seed papers):** CNN/U-Net statistical downscaling; SRCNN
precipitation; GAN downscaling; diffusion downscaling and CorrDiff; perfect prognosis versus MOS;
U-Net postprocessing; variance under-representation and underdispersion; stochastic downscaling;
inflation and randomisation; quantile-mapping critiques; cross-validation optimism; assimilation
circularity; verification against analysis versus observations; ERA5 screen-level assimilation of
SYNOP; independent withheld stations; nudged-simulation MOS; distributional regression networks and
EMOS; permutation-invariant postprocessing; double penalty and spectra; effective resolution of
data-driven models; wind downscaling in complex terrain; station-level downscaling; representativeness
error; RCM emulators; transferability and geographic generalisation; AI-weather-model evaluation
against station observations; AIFS and AIFS-CRPS; regional AI limited-area models; Nordic and
Russian/Arctic downscaling. 1117 unique records were indexed; none carried a retraction flag; 71 are
cited here.

**Thin or empty:**
- *Assimilation circularity as a named problem* — repeated targeted queries returned largely
  off-topic results (cosmology, unrelated data-assimilation sensitivity studies). Reported above as
  gap 1 rather than papered over.
- *Verification-against-own-analysis* — no usable hits; the NWP verification literature evidently
  discusses this in textbooks and technical memoranda rather than in indexed papers.
- *Northwest Russia / Russian Arctic statistical downscaling* — nothing usable retrieved.
- *Station-level DL downscaling of AI-model forecasts for temperature and wind* — the near-empty
  intersection that constitutes the project's opportunity.

**Metadata caveats.** Two abstracts could not be retrieved (doi:10.1175/jcli-d-11-00251.1 and
doi:10.1175/jcli-d-11-00254.1) and those two are cited at title level only. One record
(doi:10.1175/mwr-d-21-0150.1) came back from OpenAlex with an arXiv source field despite an AMS
journal DOI; venue corrected from the DOI prefix in the citation table. Sixteen of the 71 cited works
are preprints, flagged inline and in the `is_preprint` column — several of the most directly relevant
papers (SwAIther-Precip, ACDF, the generalisation benchmark, CRPS-LAM) are among them, so their
results are promising but not yet peer-reviewed.
