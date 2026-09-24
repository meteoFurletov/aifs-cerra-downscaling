# Downscaling AIFS to stations in the Russian Northwest — a literature review

**Scope.** Statistical downscaling / post-processing of AI-based global ensemble forecasts
(primarily ECMWF's AIFS) to surface station locations, for the domain 55–70.5°N, 26–46°E
(Pskov and Novgorod north to Murmansk; Gulf of Finland, Ladoga, Onega, White Sea).
Constraints assumed throughout: open data only, no institutional archive access,
12 CPU cores and one 4 GB GPU.

**Basis.** Five parallel citation-graph sweeps over OpenAlex and arXiv: 3,635 unique records
retrieved, 286 unique works verified and cited, 33 of them independently surfaced by more
than one sweep. Author, year, venue and citation count for every cited work were checked
against the retrieved record rather than recalled; retraction flags were checked across the
whole pool and none were flagged. 58 of the 286 are preprints (20 %), and they are marked
as such in the citation table. The preprint share is concentrated in the newest material —
58 % of the AI-model track and 29 % of the deep-downscaling track, against 3 % of the
verification track and 19 % of post-processing. The lineages this project's baselines and
scoring rest on are refereed; the frontier it aims at is not yet.

---

## 1. What this review settles

Six things were open when it started. All six now have answers, and four of them change
the project design.

1. **Is downscaling AIFS a real research direction, or already done?** Partly done — and
   this matters. Classical post-processing has been shown to transfer to AIFS unmodified,
   and generative downscaling of AIFS already exists for precipitation. What has *not*
   been done is station-level post-processing of the AIFS **ensemble** in a boreal domain.
2. **Should the target be temperature or precipitation?** Temperature — but for a better
   reason than "precipitation is missing from the station archive". See §7.
3. **Was the earlier ERA5 negative result a coding failure?** No. It is the expected
   result, and two independent literatures predict it quantitatively. See §5.
4. **What is the honest skill expectation?** About 3% over a well-tuned classical
   baseline, not the 29% that headline numbers suggest. See §4.
5. **What is the achievable floor?** Set by representativeness error, which is 50–60% of
   total temperature MAE at these latitudes — for a 2.5 km reanalysis as much as a 31 km
   one. See §6.
6. **Does the verification protocol matter at this effect size?** It decides the result.
   Standard scoring artefacts are the same magnitude as the entire effect being chased.
   See §8.

![Two quantitative warnings from the review: the honest skill ladder, and protocol artefacts against effect size]({{artifact:art_e0a9c8ac-2786-45af-ba7a-2a1c3cea3da6}})

---

## 2. The forecast source: what AIFS is, and what it gets wrong

AIFS is a graph-neural-network encoder/decoder with a sliding-window transformer processor,
trained on ERA5 and ECMWF operational analyses, run four times daily and released under
ECMWF's open data policy (Lang et al. 2024, arXiv:2406.01465). It has been fully
operational since 25 February 2025, and the September 2025 update added physical-consistency
bounding layers that substantially improved precipitation (Moldovan et al. 2025,
arXiv:2509.18994). **The version matters**: it changes which defects remain to be corrected,
so the training archive must be version-tagged.

The ensemble variant, AIFS-CRPS, is trained directly on an "almost fair" CRPS loss — the
strictly fair CRPS degenerates as a training objective and permits pathological solutions —
and it outperforms the physics-based IFS ensemble for the majority of variables and lead
times in the medium range (Lang et al. 2026, doi:10.1038/s44387-026-00073-7). Two
consequences follow immediately:

- **Members are exchangeable by construction.** Member-identity methods — BMA weights
  (Raftery et al. 2005, doi:10.1175/MWR2906.1), member-by-member post-processing — buy
  nothing. Use mean-and-spread, or a permutation-invariant treatment of the ensemble as an
  unordered set (Hoehlein et al. 2024, doi:10.1175/AIES-D-23-0070.1).
- **The baseline is harder to beat than the IFS-era literature assumes.** A CRPS-trained
  ensemble may already be well calibrated, so the entire benchmark suite — built on
  IFS-era ensembles — may overstate what post-processing adds here.

### The documented defects

| defect | evidence | relevance here |
|---|---|---|
| Cannot reproduce sub-synoptic / mesoscale structure; lacks physical consistency, which distorts *perceived* skill because RMSE rewards blurring | Bonavita 2024, doi:10.1029/2023gl107377 (136 cit.) | the canonical statement of what a downscaling layer exists to fix |
| Effective resolution coarser than nominal grid spacing; damping worsens with lead time | Bonavita 2024; Brenowitz et al. 2025, doi:10.1029/2024gl113656 | a "0.25°" AIFS field is blurrier than 0.25° |
| Blurring is a **loss-function artefact, not architectural**: members retain roughly constant power spectra with lead time while the ensemble *mean* degrades | Mahesh et al. 2025, doi:10.5194/gmd-18-5575-2025 | **downscale members, not the mean** |
| Under-predicts hot records, over-predicts cold records; physics models still win on record-breaking extremes | Zhang et al. 2026, doi:10.1126/sciadv.aec1433 | extremes need a physics baseline for comparison |
| AIFS loses 4.9 ± 2.0% in the heat tail — but *all* systems including physics-based NWP share a conditional bias toward the distribution centre | Gabler et al. 2026, arXiv:2608.09972 (preprint) | tail failure is a general forecast-system property, not a uniquely-AI pathology |
| Stale-climatology cold bias in boreal winter over land: FourCastNet V2 Small, Pangu and ACE2 produce mean temperatures resembling climates 15–20 years earlier | Landsberg et al. 2026, doi:10.1029/2025gl119740 | **exactly this regime — and AIFS was not tested** |
| Regional skill cannot be inferred from global scores: performance varies by region and is best nearer the tropics | Olivetti & Messori 2024, doi:10.5194/gmd-17-7915-2024 | 55–70.5°N is the unfavourable end of that gradient |

The last two are the openings. A stale-climatology cold bias documented in boreal winter,
never tested on AIFS, in a domain where AI-model skill has never been verified at all.

---

## 3. Is the ground occupied?

Partly, and it is better to know precisely where.

**Occupied.** The Australian Bureau of Meteorology applied IMPROVER — its *existing*
operational post-processing system — to deterministic AIFS with **no modification to
workflows**, at 569 quality-controlled automatic weather stations, and obtained accuracy
improvements comparable to those for traditional NWP in both expected-value and
probabilistic output (Trotta et al. 2025, doi:10.1175/AIES-D-25-0037.1). Two findings
transfer directly: the classical EMOS literature is not wasted effort on an AI forecast
source, and **blending AIFS with NWP improved overall skill even when AIFS alone was not
the most accurate component** — with AIFS generally the main blend component early in the
period for temperature and dew point.

Generative downscaling of AIFS also exists: SwAIther-Precip applies lead-time-aware bias
correction plus generative super-resolution to AIFS precipitation over Switzerland, reporting
48% CRPS reduction versus raw AIFS and honestly noting ~4 km effective resolution on a 1 km
grid (Assouline et al. 2026, arXiv:2605.16163, preprint). ISTM is a diffusion emulator from
AIFS to km-scale regional reanalysis (Niu et al. 2026, doi:10.1029/2025jh001072), and
HourGlass does probabilistic *temporal* downscaling of AIFS-Single and AIFS-ENS
(Ingstad et al. 2026, arXiv:2607.11457, preprint).

Using an AI model as a downscaling tool is itself a published pattern, argued from exactly
the compute constraint in play here (Koldunov et al. 2024, arXiv:2406.17977), with a
localized fine-tuning recipe (Munir et al. 2024, arXiv:2409.07585).

**Not occupied.** Station-level *spatial* post-processing of the AIFS **ensemble** for
near-surface temperature in a **boreal / high-latitude** domain. The existing AIFS work is
deterministic (Trotta), precipitation (SwAIther), typhoon intensity (ISTM), or temporal
(HourGlass). And no AI-model verification or downscaling study of any kind exists in
northwest Russia or European high-latitude Russia — the nearest work stops at the Nordic
border.

---

## 4. The methods lineage, and the honest skill number

Post-processing means learning a statistical map from forecast to observation at a station,
from an archive of past forecast–observation pairs. Since 2005 the reference standard for
2 m temperature has been **EMOS / non-homogeneous Gaussian regression**: a Gaussian whose
mean is affine in the ensemble members and whose *variance* is affine in the ensemble
variance, fitted by minimum CRPS (Gneiting et al. 2005, doi:10.1175/MWR2904.1). It survives
because the variance link inherits flow-dependent uncertainty from the spread, and because
~5 parameters can be fitted on a short single-station record.

### The number that matters

Rasp & Lerch 2018 (doi:10.1175/MWR-D-18-0187.1) is the anchor paper — 2 m temperature at
German stations, the same variable and target type as this project. Its Table 2, read from
the PDF rather than paraphrased:

| method | CRPS, 1-yr training (K) | CRPS, 9-yr training (K) |
|---|---|---|
| raw ensemble | 1.16 | 1.16 |
| EMOS, global | 1.01 | 1.00 |
| EMOS, local | 0.90 | 0.90 |
| quantile regression forest | 0.95 | 0.81 |
| boosted EMOS, local | 0.85 | 0.80 |
| neural net (aux + embeddings) | 0.82 | 0.78 |

The network beats the raw ensemble by **29%** and the best classical benchmark by **3%**.
The paper further states that boosted EMOS *outperforms* the linear network with both
auxiliary predictors and embeddings. Any project pitch quoting 29% is quoting the wrong
comparison.

**Percentages are not comparable across papers**, and every figure must carry its baseline:
29% (Rasp & Lerch, vs raw, 1-yr training), 16.5% (Van Poecke et al. 2025,
doi:10.1175/AIES-D-24-0127.1, EUPPBench, 20 lead times jointly, vs raw), 30% (Keller et al.,
arXiv:2008.07857, Swiss stations, vs high-resolution *deterministic* output — and only 8–12%
over single-model EMOS), 11.5% (Sousa et al. 2026, arXiv:2608.12271, downscaling ERA5,
stations held out in space).

### Record length discriminates between method classes

This is the most decision-relevant result for a 144-station network of uneven record length.
Going from 1 to 9 years of training: local EMOS 0.90 → 0.90 (**saturated, gains nothing**),
QRF 0.95 → 0.81 (most data-hungry), boosted EMOS and the networks gain 4–5%. Per-station
fitting is a dead end; locally-fitted forests need long records.

### How to pool across stations — four answers

1. **Semi-local / similarity-based estimation** (Lerch & Baran 2017, doi:10.1111/rssc.12153).
   Augment each station's training data with cases from *similar* stations, similarity from
   distance functions or clustering on climatology, forecast errors, ensemble predictions and
   location. Reported to significantly outperform both standard local *and* standard regional
   estimation, to permit fitting complex models without numerical instability, and to be
   **computationally cheaper than local estimation**. No GPU needed. For this project's
   compute ceiling and record heterogeneity, the correct default.
2. **Station embeddings** (Rasp & Lerch 2018). One globally-pooled network with a learned
   low-dimensional vector per station. Structural limitation: indexed by station ID, so it
   **cannot be evaluated at a station the model never saw**.
3. **SAMOS** (Dabernig et al. 2017, doi:10.1002/qj.2975). Convert forecast and observation to
   standardised anomalies against a site- and season-specific climatology, then fit *one*
   model across all sites and seasons. Removes the site effect before regression rather than
   learning it — so it needs far less data per station and generalises anywhere a climatology
   exists. The classical answer to the pooling problem, no deep learning, no ID index.
4. **Location-conditioned architectures** (Vaughan et al. 2022, arXiv:2101.07950). A
   convolutional conditional neural process maps a gridded field *plus a location* to a
   distribution, so it predicts at arbitrary locations. Sousa et al. 2026 (arXiv:2608.12271)
   extend this with learned surface embeddings compressed from 10 m Earth-observation data,
   improving CRPS by 11.5% for 2 m temperature at stations **held out in both space and
   time** across five regions — with gains persisting when the coarse input switched from
   ERA5 to AI-model forecasts.

### What actually produces skill

Not the model class. Schulz & Lerch 2022 (doi:10.1175/MWR-D-21-0150.1) benchmarked eight
methods on six years of a convection-permitting DWD ensemble at 175 German stations and
concluded that *all* methods yield calibrated forecasts, and that **incorporating additional
meteorological predictors beyond the target variable is what produces significant skill
gains**. (Caveat: the target is wind gusts. Transfer the experimental design, not the
magnitudes.) Hoehlein et al. 2024 (doi:10.1175/AIES-D-23-0070.1) point the same way from a
different angle: most relevant ensemble information sits in a few degrees of freedom, a quiet
argument that mean-plus-spread is close to sufficient.

Two cheap additions with specific support here. **Physics constraints help most when data are
scarce** — enforcing thermodynamic consistency between temperature and humidity gave
physically consistent predictions without compromising performance (Zanetta et al. 2023,
doi:10.1175/AIES-D-22-0089.1), and dew point is ~99–100% complete in this station archive, so
the T/T_d pair is available as a constraint. And **isotonic distributional regression /
EasyUQ** (Walz et al. 2024, doi:10.1137/22M1541915; theory in Henzi et al. 2021,
doi:10.1111/rssb.12450) converts a single-valued forecast into a calibrated predictive
distribution from forecast–observation pairs alone, with essentially no tuning — the cheapest
possible baseline and nearly free to run.

### Documented failure modes: winter and coast

Every paper that stratifies reports the same two. All forecast variants perform worst in DJF
for Swiss station temperature (Keller et al., arXiv:2008.07857); a transformer trained on
>1000 stations shows dependence on distance to coast and on cold temperatures (Alerskans et
al. 2022, doi:10.1002/met.2098; bias/SD: raw NWP 0.34/1.96 °C → transformer 0.02/1.13 °C).
A Baltic-to-White-Sea domain with a continental winter has both problems simultaneously.

---

## 5. Why the earlier ERA5 result was the expected one

Earlier in this project, correcting ERA5 toward these stations produced no held-out
improvement — every method scored worse than the raw field, and a gradient-boosted model
gained +2.2% at best. Two independent literatures predict this.

**The perfect-versus-imperfect training framework.** Van der Meer et al. 2023
(doi:10.1029/2022ms003593) trained the same regional-climate-model emulator twice: once with
upscaled-RCM predictors ("perfect" framework) and once with actual GCM predictors
("imperfect"). The perfect-framework emulator reproduced the target accurately on upscaled
data but, applied to real GCM data, conserved model inconsistencies and underestimated.
Substitute reanalysis for upscaled RCM and AIFS for GCM and this is the formal analogue of
the ERA5 result. The framing goes back to the VALUE perfect-predictor experiment
(Maraun et al. 2018, doi:10.1002/joc.5877, 50+ methods, 86 European stations), which reports
that MOS performs well but **requires predictors at a resolution close to the target**, and
that inter-annual and spatial variability are under-represented by almost all methods.

**Shared information between forecast and truth manufactures skill.** Ben Bouallègue et al.
2024 (doi:10.1175/BAMS-D-23-0162.1) verified an AI model against both analyses and synoptic
observations and found the two verifications *disagree*. ERA5 assimilates screen-level SYNOP
observations, so validating an ERA5 correction against those same stations is the same
mechanism operating at full strength.

**A note on what does not exist.** No canonical paper states the assimilation-circularity
argument directly with a worked station example. Targeted searches across two independent
tracks returned largely off-topic results. The argument exists only implicitly — in VALUE's
deliberately "perfect" predictor construction, in van der Meer's controlled experiment, and
in the cross-validation critique of Maraun & Widmann 2018 (doi:10.5194/hess-22-4867-2018).
This project has already produced the empirical result that would anchor such a paper.

**The theoretical root of the variance problem** is older than the deep-learning literature
that keeps rediscovering it: an MSE-minimising regression estimates a conditional mean, whose
variance is necessarily below that of the target field, and inflating the variance corrupts
the deterministic signal (Maraun 2013, doi:10.1175/jcli-d-12-00821.1, 771 citations).
"Spectral bias" claims in recent papers are restatements of this. The practical corollary is
sharp: **any station-level downscaler trained on MSE will build in the blurring defect it
aims to fix.** A Nordic stretched-grid model trained on CRPS in grid-point *and spectral*
space shows the spectral component is *necessary* for spatially coherent fields — not
achieved with MSE, nor with grid-point-only CRPS (Nordhagen et al. 2025, arXiv:2511.23043,
preprint). Subich et al. (arXiv:2501.19374, preprint) show a parameter-free spherical-harmonic
loss modification, applied by fine-tuning GraphCast, raised effective resolution from 1250 km
to 160 km.

---

## 6. The error floor: representativeness

This is the single most important quantitative result in the review, and it reframes what
"success" means.

Kołtzow et al. 2022 (doi:10.33265/polar.v41.8002) estimate median 2 m temperature
representativeness error at **50–60% of total MAE for most months in *both* CARRA (2.5 km)
and ERA5 (~31 km)**, rising to 40–55% (CARRA) and 60–70% (ERA5) for 10 m wind speed —
approximated empirically from 15 station pairs 0.5–3.0 km apart and 44 pairs 10–30 km apart.
Resolution does not fix it. A 12× finer grid did not reduce the representativeness fraction.

Göber et al. 2008 (doi:10.1002/met.78) make the same point from the verification side: a
"perfect model", constructed by grid-box-averaging dense observations, **still verifies badly
against the point observations it was built from**, with the error from wrong-kind
verification of order the forecast error itself. The comparison baseline should be the
perfect-model score, not the theoretical best.

Together these mean the earlier 1.31 K ERA5 RMSE was probably **near-optimal rather than a
failed method** — and that any claim of skill must be stated against an estimated floor, not
against zero.

The cheap baseline to beat is also from Kołtzow: a simple 0.65 °C/100 m height correction
applied before computing MAE reduces errors by 10–15% in summer in both CARRA and ERA5
(general method: Sheridan et al. 2010, doi:10.1002/met.177). Given that station-minus-model
orography here spans −128 to +72 m (σ ≈ 29 m), this is the minimum bar.

**And this is a research opening, not just a constraint.** No retrieved paper treats
station-minus-model orography mismatch as an explicit, physically-interpretable predictor
with skill reported *stratified* by it. The literature handles the mismatch by learning an
ID-indexed embedding, by standardising it away, or via hand-built terrain descriptors. The
land/water-misclassification case — 15 of 144 stations sit on cells the model calls water —
**appears in no retrieved paper at all**.

---

## 7. The regional physics: what to engineer

The regional sweep found no downscaling study inside the box, but it found something more
useful: quantified physics for the features worth building.

**Gulf of Finland snow bands** are simulated and quantified for this exact domain
(Mazon et al. 2015, doi:10.3402/tellusa.v67.25102): a quasi-stationary precipitation line
>300 km long, easterly winds 12–14 m/s, fetch 200–300 km, ~18 K land–sea potential
temperature contrast driving colliding land breezes from the Finnish and Estonian coasts,
sea-level convergence of Δv ≈ 16 m/s across ~7 km, and two coastal low-level jets with
13–14 m/s cores at 500–800 m. Bands form above 10 m/s and for V/L between 0.02–0.09 m/s/km.
This paper names the predictors: distance to water, water surface temperature, ice cover,
land–water thermal contrast, and wind direction relative to the gulf axis. None are
speculative. A related Finnish sea-effect case delivered 73 cm of snow in under a day over a
very small footprint (doi:10.5194/asr-14-231-2017) — the clearest single argument for
downscaling a 0.25° field here.

**Lakes are first-order, not a refinement.** Adding FLake to the ECMWF IFS changes
near-surface temperature forecasts (Balsamo et al. 2012, doi:10.3402/tellusa.v64i0.15829);
HIRLAM experiments show different lake-surface-temperature and ice-cover treatments give
different screen-level temperatures locally (doi:10.60910/mc88-ndnz); misrepresented
frozen-surface properties drive 2 m temperature MAE to 1.5 °C at +15 h
(doi:10.5194/gmd-11-3347-2018). This bears directly on Ladoga and Onega. Open routes to lake
state exist despite no institutional access: a 35-year AVHRR lake-surface-water-temperature
record for European lakes (doi:10.3390/rs10070990) and satellite-altimetry water-level series
for Ladoga and Onega specifically (doi:10.3390/rs14030659).

**The winter stable boundary layer is where the systematic signal is.** Nocturnal
boundary-layer temperature errors over Europe and Finland (Atlaskin & Vihma 2012,
doi:10.1002/qj.1885), why stably stratified conditions are systematically hard
(doi:10.1002/jame.20013), the community review of stable boundary layers as a model challenge
(doi:10.1175/bams-d-11-00187.1), and the radiosonde climatology of Arctic surface-based
inversion frequency, depth and strength (doi:10.1175/2011jcli4004.1). Yet **no retrieved
station post-processing study conditions its predictive distribution on inversion strength or
snow cover, or allows a bimodal predictive distribution for inversion-breakup timing.**
Mixture models exist (Jobst et al. 2024, arXiv:2412.09583) but have not been applied to this.
A physically-motivated, cheap, and genuinely novel contribution.

**Urban heat is large and not capturable from land cover alone.** At Apatity (67.567°N,
33.393°E) the winter warm anomaly reaches 11 K instantaneously with a 1.9 K wintertime mean,
at least half attributable to the UHI and that driven mostly by **direct anthropogenic
heating** (Varentsov et al. 2018, doi:10.5194/acp-18-17573-2018) — an effect as large as
projected 21st-century regional warming. St Petersburg, the largest city in the box, is
essentially undocumented for UHI. The realistic open route to urban observations is
crowdsourced citizen weather stations, validated in a Russian megacity by the same group
(doi:10.1088/1755-1315/611/1/012055; doi:10.3389/fenvs.2021.716968).

**On precipitation.** CERRA — a 5.5 km HARMONIE-based regional reanalysis over Europe
1984–2021 under Copernicus C3S, with a 10-member 11 km ensemble and an offline CERRA-Land
surface analysis, showing added value over ERA5 for almost all surface variables
(Ridal et al. 2024, doi:10.1002/qj.4764) — is the candidate precipitation truth source, and
would reopen the variable question. Two caveats. Its **eastern boundary is not pinned in the
published description**, and whether the 5.5 km grid reaches 46°E across the full 55–70.5°N
span (and how many of the 144 stations fall on interior rather than boundary-relaxation
points) is the cheapest high-value check available. And it assimilates local surface
observations rescued from national archives — so expect the ERA5/SYNOP circularity to recur
for *temperature*, which does not undermine using it for precipitation.

---

## 8. The verification protocol — and why it decides the result

At this project's measured effect size (~2%), protocol errors are the same magnitude as the
effect. Three results dominate.

**1. The standard ensemble CRPS estimator is biased by exactly 1/M.** The "unfair" estimator
inflates the expected score of a *perfectly calibrated* M-member ensemble by a factor
(1+1/M), independent of the distribution. At 51 members that is **1.96% — equal to the entire
+2.2% best gain measured in this project**. An unfair score would decide the result on its
own. The concept is Ferro 2013 (doi:10.1002/qj.2270) with the CRPS-specific magnitude in
Ferro et al. 2008 (doi:10.1002/met.45); the sweep derived the exact law analytically and
confirmed it by Monte Carlo (M=2: 50.10±0.06% vs exact 50%; M=51: 1.88±0.12% vs exact 1.96%).
Note the reflexive point: AIFS-CRPS was itself trained against a finite-ensemble-aware
objective (arXiv:2412.15832, preprint).

**2. RMSE is consistent for the conditional mean** (Gneiting 2011,
doi:10.1198/jasa.2011.r10138), so the RMSE-optimal field is smooth *by construction*.
"Should I use RMSE or MAE" silently decides what the model is asked to predict — this is the
mechanism behind AI-model blurring, not a coincidence. WeatherBench 2 (Rasp et al. 2024,
doi:10.1029/2023ms004019) documents the consequence empirically: blurring lowers RMSE while
the SEEPS categorical score **reverses the model ranking**. And deterministic skill ranking
does not carry over to probabilistic skill — a model that wins on RMSE can lose on CRPS
(Brenowitz et al. 2025, doi:10.1029/2024gl113656).

**3. Pooling manufactures skill.** Skill scores can be inflated purely by variation in the
underlying climatology across pooled samples (Hamill & Juras 2006, doi:10.1256/qj.06.25).
With 144 stations spanning 55–70.5°N and a strong seasonal cycle, pooling against a single
climatological reference would produce skill unrelated to the model.

### Protocol checklist

- **Fair scores throughout.** Non-negotiable at this effect size.
- **Spread–skill target is √((M+1)/M), not 1.0** (Fortin et al. 2014,
  doi:10.1175/jhm-d-14-0008.1) — 1.0097 at M=51, but 1.049 at M=10 and 1.095 at M=5.
  Comparing to 1.0 makes every finite ensemble look underspread.
- **Sharpness subject to calibration** (Gneiting et al. 2007,
  doi:10.1111/j.1467-9868.2007.00587.x): calibration is a constraint, sharpness the
  objective. A merely wider forecast is not better.
- **CORP reliability diagrams, not binned ones** (Dimitriadis et al. 2021,
  doi:10.1073/pnas.2016191118) — isotonic regression instead of binning, reproducible, with
  a consistent decomposition and uncertainty bands.
- **Rank histograms per station or per homogeneous group, never pooled.** Correlated
  verification samples distort them even for a perfectly calibrated system
  (Marzban et al. 2010, doi:10.1175/2010mwr3129.1); pooling 144 stations produces an unearned
  U-shape.
- **hv-block cross-validation with a genuine buffer** (Racine 2000,
  doi:10.1016/s0304-4076(00)00030-0) — deleting observations on *each side* of the held-out
  block is the step most practitioners omit — and hyperparameter tuning nested *inside* the
  spatial CV (Schratz et al. 2019, doi:10.1016/j.ecolmodel.2019.06.002). CV strategy changes
  both measured performance *and* model interpretation (Sweet et al. 2023,
  doi:10.1175/aies-d-23-0026.1); Roberts et al. 2016 (doi:10.1111/ecog.02881) is the clearest
  statement of the double-leak problem. Match the CV design to the intended inference —
  spatial CV is not automatically correct and is pessimistically biased for area-average
  accuracy (Wadoux et al. 2021, doi:10.1016/j.ecolmodel.2021.109692).
- **Report held out in space *and* in time.** Rare in the literature and it costs nothing but
  discipline.
- **False-discovery-rate control across 144 stations** (Wilks 2016,
  doi:10.1175/bams-d-15-00267.1). Testing 144 stations at the 5% level yields ~7 spurious
  significant results by chance. Diebold–Mariano tests with autocorrelation-aware effective
  sample size (Diebold 2015, doi:10.1080/07350015.2014.983236) — station temperature errors
  are strongly autocorrelated at 3-hourly resolution (Möller & Groß 2019,
  doi:10.1002/qj.3667).
- **Never select verification cases by observed outcome.** Scoring only the cold days
  destroys propriety and favours forecasters who exaggerate — the forecaster's dilemma
  (Lerch et al. 2017, doi:10.1214/16-sts588). Use weighted proper scores for extremes
  (Taillardat et al. 2022, doi:10.1016/j.ijforecast.2022.07.003).
- **Fix the interpolation scheme in advance and report it.** Bilinear versus
  nearest-neighbour averaging alone materially changes skill scores
  (Accadia et al. 2003, doi:10.1175/1520-0434(2003)018<0918:sopfss>2.0.co;2) — a
  methodological choice of comparable magnitude to this project's entire effect size.
- **For AIFS-vs-IFS claims, use the potential CRPS** (Gneiting et al. 2025,
  arXiv:2506.03744, preprint): subject the deterministic backbone of both model types to the
  same post-processing before comparing, separating "carries more information" from "happens
  to be better calibrated out of the box".

---

## 9. What is actually open

Consolidating across all five sweeps, ranked by how well-posed and how reachable they are on
12 cores and a 4 GB GPU.

1. **Station-verified AIFS ensemble evaluation at 55–70.5°N.** Nothing exists. Published
   global skill has never been shown to transfer to these latitudes, and the one paper that
   stratifies by region reports skill is best nearer the tropics. This is a contribution
   *before* any downscaling, and it is nearly free once the archive is cached.
2. **The stale-climatology cold bias, tested on AIFS.** Documented for FourCastNet, Pangu and
   ACE2 in boreal winter over land, 15–20 year lag; AIFS not tested. Answerable with station
   data.
3. **Representativeness error as an explicit, stratified term.** Elevation offset and
   land/water misclassification as physically-interpretable predictors, with skill reported
   stratified by them and against an estimated floor. Methodological, not merely regional —
   and the land/water case appears in no retrieved paper.
4. **Inversion-conditional post-processing.** Condition the predictive distribution on
   inversion strength, snow cover and cloud; allow bimodality for inversion-breakup timing.
   The error is known to be structured, seasonal and conditional; nobody has exploited it at
   station level in any domain.
5. **Does classical post-processing still add value on top of a CRPS-trained ensemble?** The
   whole benchmark suite predates AIFS-CRPS. Open, cheap, and of general interest.
6. **Members versus mean at station level.** Members retain spectra while the mean degrades,
   but no paper compares downscaling members against downscaling the mean at stations with
   proper scores. A well-posed experiment that fits the hardware.
7. **The compute-constrained regime.** Every winning method in the literature is reported
   from an institutional setting. Nothing asks what the best achievable station-level skill
   is on 12 cores, one small GPU and open data. Given that ML beats a tuned classical
   baseline by ~3%, the answer may be "almost all of it" — useful to the large community
   without institutional access.
8. **Ladoga and Onega mesoscale meteorology.** Europe's two largest lakes, in the middle of
   the domain, with no mesoscale modelling study found. Whether a 0.25° AI forecast
   represents any of the quantified land–water contrast signal is unasked and well-posed.

---

## 10. What this implies for the project design

Stated as an ordered build, because the ordering is itself a review finding.

1. **De-risk on EUPPBench first** (Demaeyer et al. 2023, doi:10.5194/essd-15-2635-2023):
   publicly available time-aligned ECMWF ensemble forecasts and station observations with a
   published 2 m temperature baseline suite. Reproducing a published number converts "is my
   code correct?" from unanswerable into checkable — before pointing the pipeline at a
   bespoke ISD-Lite/AIFS archive where every discrepancy has two possible causes.
2. **Fix the verification protocol before the first model.** Fair CRPS, hv-block CV with
   buffer, per-station rank histograms, FDR control, a declared interpolation scheme, and an
   estimated representativeness floor. At a 2% effect size this is not housekeeping.
3. **Baselines, in this order:** raw AIFS ENS → height-corrected AIFS (0.65 °C/100 m) →
   EasyUQ/IDR → global EMOS → semi-local EMOS → boosted EMOS. The last is the number to
   beat, and it is the one most projects skip.
4. **Then one ML model, not four.** A distributional regression network with auxiliary
   predictors, pooled semi-locally rather than per-station. Trained on CRPS, never MSE.
5. **Include an AIFS+IFS blend as a first-class candidate**, not an afterthought — blending
   beat picking in the only comparable study, and both ensembles are available at 0.25°.
6. **Engineer the features the regional physics names:** elevation offset, land/water
   misclassification flag, distance to water, lake/sea surface temperature and ice cover,
   land–water thermal contrast, wind direction relative to the Gulf axis, snow depth,
   inversion proxy, and an urban indicator.
7. **Report against the floor, stratified by station class and season**, with held-out-in-
   space as well as held-out-in-time. The negative results are part of the contribution.

---

## 11. Coverage limits and honest caveats

**Russian-language literature is under-represented, and this bounds the novelty claim.**
All searches were English-language via OpenAlex and arXiv. OpenAlex indexing of Roshydromet
institutional journals (*Meteorologiya i Gidrologiya* and similar) is patchy. The
COSMO-Ru and Roshydromet-archive negatives should be read as *absent from the indexed
international literature*, which is weaker than *does not exist*. **You are far better placed
than these databases to close this gap, and should check before claiming domain novelty.**

**The regional negative is evidenced, not assumed.** No downscaling or post-processing study
verified against stations inside 55–70.5°N/26–46°E was found in any vocabulary tried: 77
keyword queries across seven vocabulary families, 24 citation-graph traversals, 5 arXiv
queries and 10 deliberate negative-confirmation queries over 1,623 unique records. The
failure modes are instructive — "northwest Russia" matched the US Pacific Northwest (1,110
records), and a Leningrad/Novgorod/Pskov query returned 9 records topped by forest carbon and
plant fungi.

**Preprint dependence.** 58 of 286 cited works are preprints (20 %) — a minority of the pool,
but they are concentrated exactly where this project's design decisions land, and several
load-bearing ones are unrefereed: SwAIther-Precip, HourGlass, the station-based extremes
verification, both Nordic stretched-grid papers, the potential-CRPS framework, MIXSAMOS-GB,
the EO-embedding downscaler. Their numbers are promising but unrefereed. The classical
post-processing and verification lineages this project's baselines rest on are peer-reviewed.

**The strongest ML benchmark is the wrong variable.** The eight-method systematic comparison
targets *wind gusts*. The best-quantified temperature comparison remains Rasp & Lerch 2018 —
a 2018 paper on a 2007–2016 archive. No post-2022 study retrieved re-runs that benchmark
suite on temperature.

**Metadata problems that could mislead.** Citation counts are OpenAlex counts at retrieval
time and are absent for arXiv-only records, which structurally undercounts the newest and
most relevant work. Abstracts were missing for a number of AMS and Nature-family records, so
some quantitative detail came from the corresponding arXiv abstracts. Two lake papers under
DOI prefix 10.60910 returned plainly wrong OpenAlex year and venue metadata; titles, authors
and citation counts are consistent with real works, so the science is cited but year and
venue were blanked and need the publisher record. Two Journal-of-Climate downscaling papers
(doi:10.1175/jcli-d-11-00251.1, doi:10.1175/jcli-d-11-00254.1) are cited at title level only.
CERRA full text was not retrievable (publisher 403), leaving its eastern boundary an explicit
verification task.

**Deliberately out of scope:** precipitation post-processing surveyed only at entry-point
level (doi:10.1002/wat2.1246, doi:10.1175/WAF-D-18-0149.1), pure climate emulation except
where it bears on the stale-climatology bias, nowcasting, and non-ECMWF operational AI
systems beyond the comparison set.

**Where numbers were read from full text rather than abstracts:** Rasp & Lerch Table 2, the
Trotta AIFS/IMPROVER findings, the Kołtzow representativeness fractions, the Bonavita spectral
analysis, WeatherBench 2, and AIFS-CRPS. The 1/M CRPS inflation law is a derivation with
Monte Carlo verification, consistent with but not quoted from Ferro 2013 / Ferro et al. 2008.
