# Annotated reading order

Thirty papers in four tiers. The ordering is deliberate: each tier makes the next one
readable. Tier 1 is a weekend; Tier 2 is the working core; Tiers 3–4 are read as the
build reaches them.

Preprints are marked **[P]** — not yet peer-reviewed, treat numbers as provisional.

---

## Tier 1 — Read before writing any code (6 papers)

These six determine what "success" can even mean for this project. Read them in order.

**1. Gneiting, Balabdaoui & Raftery (2007), *JRSS-B*, doi:10.1111/j.1467-9868.2007.00587.x —
Probabilistic Forecasts, Calibration and Sharpness.**
The organising principle of the whole evaluation: maximise sharpness *subject to*
calibration. Calibration is a constraint you must satisfy; sharpness is the objective.
Every later protocol decision references this asymmetry. Short.

**2. Ferro (2013), *QJRMS*, doi:10.1002/qj.2270 — Fair scores for ensemble forecasts.**
Changes your code on day one. An unfair score rewards a system for having more members; a
fair score rewards it only for being right. At 51 members the artefact is 1.96% — the size
of this project's entire measured gain. Follow with Ferro et al. 2008 (doi:10.1002/met.45)
for the magnitude.

**3. Kołtzow et al. (2022), *Polar Research*, doi:10.33265/polar.v41.8002 — Value of CARRA
in representing near-surface temperature and wind speed in the north-east European Arctic.**
Read the representativeness section closely. It quantifies the floor — 50–60% of total
temperature MAE, for a 2.5 km reanalysis as much as a 31 km one — and shows how to estimate
it empirically from station pairs. It tells you what you should have been comparing against,
and it means the earlier 1.31 K ERA5 result was near-optimal rather than a failure.

**4. Göber, Zsótér & Richardson (2008), *Met. Apps*, doi:10.1002/met.78 — Could a perfect
model ever satisfy a naive forecaster?**
Short, and it permanently reframes verification. A perfect model built by grid-box-averaging
dense observations still verifies badly against the point observations it came from, and the
error grows with event severity. Read straight after Kołtzow so the numbers land.

**5. Vannitsem et al. (2020), *BAMS*, doi:10.1175/BAMS-D-19-0308.1 — Statistical
Postprocessing for Weather Forecasts: Review, Challenges, and Avenues in a Big Data World.**
The field map: taxonomy of methods, verification practice, and an explicit statement of the
open problems. Read for orientation, not detail — most of Tier 2 is a specialisation of
something introduced here.

**6. Koldunov et al. (2024), arXiv:2406.17977 **[P]** — Emerging AI-based weather prediction
models as downscaling tools.**
Your own instinct, already in the literature, with the explicit argument for why it is right
under compute constraints: high-resolution models are prohibitively expensive and
conventional downscaling is region-limited. Pair with Munir et al. (arXiv:2409.07585) **[P]**
for the localized fine-tuning pattern that fits a 4 GB GPU.

---

## Tier 2 — The working core (9 papers)

**7. Rasp & Lerch (2018), *MWR*, doi:10.1175/MWR-D-18-0187.1 — Neural Networks for
Postprocessing Ensemble Weather Forecasts.**
The paper to read most carefully — same variable (2 m temperature), same target type
(stations). Introduces station embeddings in a globally-pooled network. **Read Table 2 line
by line**: it gives the ML-over-raw gain (29%), the honest ML-over-boosted-EMOS gain (3%),
and the record-length sensitivity of each method class — the last being the most
decision-relevant result for a 144-station network of uneven record length.

**8. Trotta et al. (2025), *AIES*, doi:10.1175/AIES-D-25-0037.1 — Statistical Postprocessing
Yields Accurate Probabilistic Forecasts from Artificial Intelligence Weather Models.**
The project's closest precedent and the most strategically important result available. A
national met service applied its *existing* operational system to AIFS with no workflow
modification and got gains comparable to those on traditional NWP. Establishes that the
classical EMOS literature transfers as-is, and that a blend beats picking.

**9. Lerch & Baran (2017), *JRSS-C*, doi:10.1111/rssc.12153 — Similarity-based semi-local
estimation of EMOS models.**
Directly answers this project's central design question. Augment each station's training data
with cases from similar stations. Reported to significantly outperform both standard local
and standard regional estimation, to permit fitting complex models without numerical
instability, and to be *computationally cheaper* than local estimation. For 144 stations of
uneven record length on 12 cores, this is the correct default.

**10. Gneiting (2011), *JASA*, doi:10.1198/jasa.2011.r10138 — Making and Evaluating Point
Forecasts.**
Read for one idea with large consequences: RMSE is consistent for the conditional mean, so
the RMSE-optimal field is smooth by construction. This is the mechanism behind AI-model
blurring.

**11. Maraun (2013), *J. Climate*, doi:10.1175/jcli-d-12-00821.1 — Bias Correction, Quantile
Mapping, and Downscaling: Revisiting the Inflation Issue.**
The theoretical root of the variance argument, 771 citations. An MSE-minimising regression is
a conditional-mean estimator with deficient variance, and inflating the variance corrupts the
deterministic signal. Read before any generative method so "spectral bias" claims register as
restatements of a known result.

**12. Lang et al. (2024), arXiv:2406.01465 **[P]** — AIFS: ECMWF's data-driven forecasting
system.**
The primary AIFS paper. Read with the September 2025 update (Moldovan et al.,
arXiv:2509.18994 **[P]**) so you know which AIFS version you are downloading — it changes
which defects remain to be corrected. Then Lang et al. 2026
(doi:10.1038/s44387-026-00073-7) for AIFS-CRPS, the ensemble you would actually downscale.

**13. Bonavita (2024), *GRL*, doi:10.1029/2023gl107377 — On Some Limitations of Current
Machine Learning Weather Prediction Models.**
The canonical statement of the defect a downscaling layer exists to fix: AI models cannot
properly reproduce sub-synoptic and mesoscale phenomena and lack physical consistency, which
distorts their *perceived* skill because RMSE rewards blurring. 136 citations; the paper the
rest of the error-mode literature responds to.

**14. Demaeyer et al. (2023), *ESSD*, doi:10.5194/essd-15-2635-2023 — The EUPPBench
postprocessing benchmark dataset v1.0.**
The practical de-risking step, and the reason to read it early rather than late. Fit the
pipeline here first and reproduce a published number — it converts "is my code correct?" from
unanswerable into checkable, before pointing anything at a bespoke archive where every
discrepancy has two possible causes.

**15. Mazón et al. (2015), *Tellus A*, doi:10.3402/tellusa.v67.25102 — Snow bands over the
Gulf of Finland in wintertime.**
The physics of your domain, quantified: >300 km bands, 12–14 m/s easterlies, 200–300 km
fetch, ~18 K land–sea potential temperature contrast, colliding land breezes with Δv ≈ 16 m/s
convergence over ~7 km. This is the paper that names your features — distance to water, water
surface temperature, ice cover, land–water thermal contrast, wind direction relative to the
gulf axis — and none of them are speculative.

---

## Tier 3 — Read as the build reaches them (9 papers)

**Methods and pooling**

**16. Gneiting et al. (2005), *MWR*, doi:10.1175/MWR2904.1 — Calibrated Probabilistic
Forecasting Using Ensemble Model Output Statistics.** The EMOS original. Read for the
variance link, which is why the method survived twenty years.

**17. Messner et al. (2017), *MWR*, doi:10.1175/MWR-D-16-0088.1 — Nonhomogeneous Boosting
for Predictor Selection.** The strongest non-neural benchmark in the literature and the one
classical model this project must fit — it is the "3%" denominator in Rasp & Lerch.

**18. Dabernig et al. (2017), *QJRMS*, doi:10.1002/qj.2975 — Standardized anomaly model
output statistics over complex terrain.** Pooling without deep learning and without an
ID index. Convert to standardised anomalies against a site- and season-specific climatology,
then fit one model everywhere. Generalises to stations the model never saw.

**19. Schulz & Lerch (2022), *MWR*, doi:10.1175/MWR-D-21-0150.1 — Machine Learning Methods
for Postprocessing Ensemble Forecasts of Wind Gusts.** The experimental design to copy, and
the source of the finding that auxiliary predictors matter more than model class.
**Caveat: the target is wind gusts — take the methodology, not the magnitudes.**

**20. Vaughan et al. (2022), arXiv:2101.07950 **[P]** — Convolutional conditional neural
processes for local climate downscaling.** The architectural answer to the unseen-station
problem: map a gridded field plus a *location* to a distribution, rather than looking up a
station index. Then Sousa et al. 2026 (arXiv:2608.12271) **[P]** for learned surface
embeddings and the held-out-in-space result.

**Verification**

**21. Rasp et al. (2024), *JAMES*, doi:10.1029/2023ms004019 — WeatherBench 2.** The reference
protocol for data-driven models, including the empirical fact that blurring lowers RMSE while
SEEPS reverses the ranking.

**22. Hamill & Juras (2006), *QJRMS*, doi:10.1256/qj.06.25 — Measuring forecast skill: is it
real skill or is it the varying climatology?** Read before aggregating anything across 144
stations spanning 15 degrees of latitude.

**23. Roberts et al. (2016), *Ecography*, doi:10.1111/ecog.02881 — Cross-validation
strategies for data with temporal, spatial, hierarchical, or phylogenetic structure.** Not
meteorology, but the clearest statement of the double-leak problem you face. Pair with
Sweet et al. 2023 (doi:10.1175/aies-d-23-0026.1), which shows on climate data that CV
strategy changes both skill *and* feature importances.

**24. Fortin et al. (2014), *J. Hydrometeorology*, doi:10.1175/jhm-d-14-0008.1 — Why should
ensemble spread match the RMSE of the ensemble mean?** The spread–skill target is
√((M+1)/M), not 1.0. Two pages of consequence.

---

## Tier 4 — Context and alternatives (6 papers)

**25. Maraun et al. (2018), *IJC*, doi:10.1002/joc.5877 — VALUE perfect predictor experiment
synthesis.** 50+ methods, 86 European stations. Frames the perfect-prognosis vs MOS question
and reports that inter-annual and spatial variability are under-represented by almost all
methods.

**26. van der Meer et al. (2023), *JAMES*, doi:10.1029/2022ms003593 — Deep Learning Regional
Climate Model Emulators: A Comparison of Two Downscaling Training Frameworks.** The closest
thing to a controlled demonstration that perfect-framework skill does not transfer. The
formal analogue of this project's ERA5 finding.

**27. Assouline et al. (2026), arXiv:2605.16163 **[P]** — SwAIther-Precip.** The closest
existing work to your stated idea, and proof the ground is partly occupied: AIFS downscaled
to km scale, bias-corrected at coarse resolution first, then a cheap super-resolution stage
trained *directly on observations*. The lead-time-aware training lesson transfers; the
precipitation target does not.

**28. Nordhagen et al. (2025), arXiv:2511.23043 **[P]** — High-Resolution Probabilistic
Data-Driven Weather Modeling with a Stretched-Grid.** Read for one design lesson that decides
whether a downscaler works: the *spectral* component of the CRPS loss is necessary for
spatially coherent fields, and is achieved neither by MSE nor by grid-point-only CRPS.

**29. Ridal et al. (2024), *QJRMS*, doi:10.1002/qj.4764 — CERRA, the Copernicus European
Regional Reanalysis system.** The candidate solution to the precipitation truth-data problem:
5.5 km, 1984–2021, Copernicus-licensed. Read it to decide whether the problem is solvable —
then verify the eastern boundary yourself, since the paper does not pin it.

**30. Varentsov et al. (2018), *ACP*, doi:10.5194/acp-18-17573-2018 — Anthropogenic and
natural drivers of a strong winter urban heat island in a typical Arctic city.** The only
quantified UHI study inside your box (Apatity): up to 11 K instantaneous, 1.9 K winter mean,
at least half attributable to the UHI and that driven mostly by *direct anthropogenic
heating*. Gives a defensible magnitude prior — and warns that land-cover features alone will
not capture it.

---

## If you only read three

Kołtzow et al. (doi:10.33265/polar.v41.8002) for the floor,
Rasp & Lerch (doi:10.1175/MWR-D-18-0187.1) for the method and the honest number,
Trotta et al. (doi:10.1175/AIES-D-25-0037.1) for the precedent.
