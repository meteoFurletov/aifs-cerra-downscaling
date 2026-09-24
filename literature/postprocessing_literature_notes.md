# Statistical and ML Post-processing of Ensemble Forecasts to Station Locations

**Literature track: classical-to-modern lineage, with emphasis on 2 m temperature and multi-station design.**
Prepared for a downscaling project over NW Russia (55–70.5 N, 26–46 E; 144 ISD-Lite stations; AIFS ENS / IFS ENS at 0.25°; local compute only).

All numbers below are quoted from the papers themselves — either from the abstract or from the results table, with the source stated. Where a paper claims an improvement without an anchor, I say so rather than inventing one.

---

## 0. The one-paragraph orientation

Post-processing means: learn a statistical map from *forecast* to *observation* at a location, from a training archive of past forecast–observation pairs. Since 2005 the field's standard answer for temperature has been **EMOS / non-homogeneous Gaussian regression** — fit a Gaussian whose mean is affine in the ensemble members and whose *variance is affine in the ensemble variance*, by minimising CRPS. Everything since is either (a) a better regression function (boosting, forests, neural nets), (b) a more flexible predictive distribution (quantile functions, mixtures, non-parametric), or (c) a better answer to *how do you share information across stations*. The last one is the user's actual problem, and it is where the most useful recent work sits.

The honest headline: **ML beats the raw ensemble by a lot, and beats a well-tuned classical EMOS by a little.** In the canonical study the neural network's edge over the strongest classical benchmark was 3%, against 29% over the raw ensemble. Any project plan should budget for the 3%, not the 29%.

---

## 1. The classical lineage — what it is and why the shape of it matters

**Model Output Statistics** begins with Glahn & Lowry 1972 (doi:10.1175/1520-0450(1972)011<1203:TUOMOS>2.0.CO;2): regress the observed variable on NWP output *at the station*, so the regression absorbs both model bias and the unresolved local effect in one step. This is still exactly what the user will be doing. The distinction that matters historically is MOS vs "perfect prog": MOS is trained on the *forecast* field at the forecast lead time, so it learns lead-time-dependent bias — which is why post-processing coefficients are normally fitted separately per lead time.

**EMOS / NGR** (Gneiting et al. 2005, doi:10.1175/MWR2904.1) is the reference standard for 2 m temperature and remains so. Its predictive distribution is
N(a + b₁x₁ + … + b_m x_m , c + d·S²), where S² is the ensemble variance, fitted by minimum CRPS. Two features explain its longevity: the variance link means the model inherits flow-dependent uncertainty from the ensemble spread (rather than a climatological spread), and it has ~5 parameters, so it can be fitted on a short archive at a single station. For a Gaussian, CRPS has a closed form and hence an analytic gradient — which is also why it became the natural loss for the neural-net generation.

**Bayesian Model Averaging** (Raftery et al. 2005, doi:10.1175/MWR2906.1) is the main alternative: the predictive density is a weighted mixture of kernels, one per member, with weights reflecting member skill. Sloughter/Wilson-style operational BMA for surface temperature followed (Wilson et al. 2007, doi:10.1175/MWR3347.1). For a single exchangeable-member ensemble like AIFS ENS, BMA's per-member weights buy nothing — the members are statistically indistinguishable by construction. **Recommendation: skip BMA for this project.** Fraley et al. 2010 (doi:10.1175/2009MWR3046.1) is the paper to read if you nonetheless need to handle exchangeable groups or *missing* members, which is a realistic archive problem.

**The evaluation framework** is as important as the methods, and the user should internalise it before fitting anything. Gneiting & Raftery 2007 (doi:10.1198/016214506000001437) establishes proper scoring rules and CRPS; Gneiting, Balabdaoui & Raftery 2007 (doi:10.1111/j.1467-9868.2007.00587.x) states the governing principle — **maximise sharpness subject to calibration**. Practically: a post-processed forecast that is merely wider is not better, and a rank histogram/PIT plot plus CRPS decomposition is the minimum reporting standard.

**Training-length behaviour** was quantified early with reforecasts: Hagedorn et al. 2008 (doi:10.1175/2007MWR2410.1) for 2 m temperature and Hamill et al. 2008 (doi:10.1175/2007MWR2411.1) for precipitation. The temperature paper is the one that tells you how much of ensemble error is systematic and correctable, and it is the reason the field's rule of thumb is that temperature needs far less training data than precipitation.

**The reviews.** Vannitsem et al. 2021, *BAMS* (doi:10.1175/BAMS-D-19-0308.1) is the field review and the single best entry point — taxonomy, verification practice, and a clear statement of open problems. Li et al. 2017 (doi:10.1002/wat2.1246) is the hydrometeorological complement, stronger on precipitation and multivariate dependence. Wilks' book chapter (doi:10.1016/B978-0-12-812372-0.00003-0) is the cleanest formal treatment of EMOS/BMA/logistic regression if the equations in the papers feel underspecified.

### 1a. The classical extensions that are still competitive

These matter because they are the *honest baselines* — several of them are hard for deep learning to beat.

- **Boosting inside NGR** (Messner et al. 2017, doi:10.1175/MWR-D-16-0088.1). Lets you throw many predictors at an EMOS model with automatic, regularised variable selection. In Rasp & Lerch this is `EMOS-loc-bst` and it is the *strongest* non-neural benchmark. **If the user fits one classical model, this should be it.**
- **Estimation choice** (Gebetsberger et al. 2018, doi:10.1175/MWR-D-17-0364.1): minimum-CRPS vs maximum-likelihood estimation for NGR. Relevant precisely because the user has short, uneven per-station records.
- **SAMOS — standardised anomaly MOS** (Dabernig et al. 2017, doi:10.1002/qj.2975). Convert both forecast and observation to standardised anomalies against a site- and season-specific climatology, then fit *one* model across all sites and seasons. This is the classical-statistics answer to pooling and it is very well matched to the user's problem: it removes the site effect *before* regression instead of learning it, so it needs far less data per station. **Strongly recommended as the pooled baseline.**
- **Time-adaptive training** (Lang et al. 2020, doi:10.5194/npg-27-23-2020): a systematic comparison of rolling-window vs seasonal-window vs weighted training schemes for NGR on central-European 2 m temperature. Directly answers "how do I handle seasonality with a short archive".
- **Temporal error structure**: Möller & Groß 2019 (doi:10.1002/qj.3667) add a heteroscedastic autoregressive term; Jobst et al. 2024 (doi:10.1002/qj.4844) build a fuller time-series EMOS with seasonality, trend and AR errors. Worth knowing because station temperature errors are strongly autocorrelated at 3-hourly resolution, and ignoring this inflates apparent significance in verification.
- **Spatial extensions**: Feldmann et al. 2015 (doi:10.1175/MWR-D-14-00210.1) and Scheuerer & König 2014 (doi:10.1002/qj.2323) on locally-adaptive spatial NGR for temperature, including comparison of Gaussian-random-field and ensemble-copula-coupling routes to spatial dependence.

### 1b. What operational centres actually run

Useful as a sanity check on ambition level.

- **DWD Ensemble-MOS** (Hess 2020, doi:10.5194/npg-27-473-2020) — the German service's operational system, with explicit treatment of extremes.
- **Météo-France** (Taillardat & Mestre 2020, doi:10.5194/npg-27-329-2020) — industrial-scale ML post-processing; notably they post-process *at stations* and then interpolate to the grid, not the reverse.
- **Met Office IMPROVER** (Roberts et al. 2023, doi:10.1175/BAMS-D-21-0273.1) — the probabilistic post-processing framework that reappears below in the AIFS test.
- **FMI** (Ylinen et al. 2020, doi:10.1002/met.1971) — operational station-specific calibration of ECMWF ENS temperature out to 240 h over Europe. **This is the closest operational analogue to the user's setup** — same forecast source, same variable, same station-level target, neighbouring domain.

---

## 2. The ML generation — and what the gains actually are

**Quantile Regression Forests** (Taillardat et al. 2016, doi:10.1175/MWR-D-15-0260.1) was the first widely-adopted break from parametric distributions: estimate quantiles non-parametrically from a random forest, using any available predictor, with no distributional assumption. Applied to Météo-France's 35-member PEARP for surface temperature and wind at 3–54 h lead times, and reported to outperform EMOS. Two properties matter for the user: QRF cannot extrapolate beyond the observed range of the training data (a real limitation for extremes), and in its standard form it is fitted *locally*, per station — which is why it degrades with short records (see the table below).

**Rasp & Lerch 2018** (doi:10.1175/MWR-D-18-0187.1) is the anchor of the modern era, and the paper the user should read most carefully. 2 m temperature at German stations; the network outputs the *parameters of a Gaussian* and is trained on the closed-form Gaussian CRPS — i.e. it is EMOS with a neural regression function. Two design ideas from this paper became standard:

1. **Station embeddings.** Each station gets a learned low-dimensional vector, trained jointly with one *globally pooled* network. This is the crucial trick: one model for all stations, but with station identity as a learned input, so the model shares statistical strength across the network while still adapting per site.
2. **Auxiliary predictors** beyond the target variable — the paper's permutation-importance analysis put the station embedding and shortwave radiation among the top features after t2m itself.

**Verified CRPS values, Table 2** (mean CRPS over calendar year 2016, K; two training-period columns):

| Model | 1 yr (2015) | 9 yr (2007–2015) |
|---|---|---|
| Raw ensemble | 1.16 | 1.16 |
| EMOS-gl (global) | 1.01 | 1.00 |
| EMOS-loc (per station) | 0.90 | 0.90 |
| **EMOS-loc-bst** (boosted, per station) | **0.85** | **0.80** |
| QRF (local) | 0.95 | 0.81 |
| FCN (linear net, no aux/emb) | 1.01 | 1.01 |
| FCN-aux | 0.92 | 0.91 |
| FCN-emb | 0.91 | 0.91 |
| FCN-aux-emb | 0.88 | 0.87 |
| NN-aux (1 hidden layer) | 0.90 | 0.86 |
| **NN-aux-emb** | **0.82** | **0.78** |

Read this table three ways, because each reading is a design lesson:

- **ML vs raw ensemble:** the paper states the best network improves on the raw ensemble by 29% (1-year training: 1.16 → 0.82). This is the number that gets quoted.
- **ML vs the best classical model:** 3% (0.85 → 0.82 on 1-year training; 0.80 → 0.78 on 9-year). **This is the honest number.** The paper says so explicitly, and also notes that boosted EMOS *outperforms* the linear network with both aux and embeddings (FCN-aux-emb) by 3%. Deep learning is not automatically ahead.
- **Sensitivity to record length:** QRF goes 0.95 → 0.81 when training grows from 1 to 9 years — it is the most data-hungry method in the table. Per-station EMOS barely moves (0.90 → 0.90). Boosted EMOS and the networks gain 4–5%. **For a user with uneven 15+ year records but 3-hourly sampling, this is the single most decision-relevant result in the paper.**

**Flexible output distributions.** Bremnes 2020 (doi:10.1175/MWR-D-19-0227.1) replaces the Gaussian with a **Bernstein quantile function** (BQN) — the net predicts coefficients of a monotone polynomial basis, giving a flexible, guaranteed-monotone quantile function without assuming a shape. Also worth knowing: histogram-estimation networks (HEN), which discretise into bins.

**The systematic comparison to trust.** Schulz & Lerch 2022, *MWR* (doi:10.1175/MWR-D-21-0150.1) benchmark eight methods — EMOS, member-by-member, isotonic distributional regression, gradient-boosted EMOS, QRF, DRN, BQN, HEN — on six years of a convection-permitting DWD ensemble against hourly observations at 175 German stations. The target is **wind gusts**, not temperature, so transfer the *methodology* not the magnitudes. Their conclusions that do generalise: all methods produce calibrated forecasts; **the dominant gain comes from adding auxiliary meteorological predictors, not from the choice of model class**; and locally-adaptive neural networks with flexible output distributions come out on top. If the user reads one methods-comparison paper, this is it — the experimental design is the template to copy.

**Architectural developments worth knowing:**

- **Permutation-invariant networks** (Höhlein et al. 2024, doi:10.1175/AIES-D-23-0070.1): treat the ensemble as an unordered *set* of members rather than as summary statistics. Their importance analysis found most of the relevant information sits in a few ensemble-internal degrees of freedom — which is a quiet argument that mean + spread is nearly sufficient, and that elaborate member-level architectures may not pay for themselves.
- **Transformers, station-trained** (Alerskans et al. 2022, doi:10.1002/met.2098): 2 m temperature from >1000 private weather stations in Denmark, validated on independent DMI SYNOP stations. Reported bias / STD: raw NWP 0.34 / 1.96 °C, linear regression 0.03 / 1.63, NN 0.10 / 1.53, transformer 0.02 / 1.13 °C. **They report a dependence on distance to the coast and on cold temperatures** — a direct warning for a Baltic/White Sea domain with severe winters.
- **Transformers, all lead times jointly** (Van Poecke et al. 2025, doi:10.1175/AIES-D-24-0127.1): one model across 20 lead times with up to fifteen predictors, on EUPPBench. Reported CRPS improvement over the raw forecast of **16.5% for 2 m temperature**, 10% for 10 m wind, 9% for 100 m wind, beating a member-by-member benchmark and running up to 6× faster. Note the contrast with Rasp & Lerch's 29% — different ensemble, different domain, different baseline. This is exactly why cross-paper percentage comparisons are unsafe.
- **Physics-constrained networks** (Zanetta et al. 2023, doi:10.1175/AIES-D-22-0089.1): enforce thermodynamic state equations so temperature and humidity predictions stay mutually consistent. Physical consistency at no cost in skill, and **"especially advantageous when data are scarce"** — relevant to a data-poor domain, and the user has dew point at ~99–100% completeness, so the T/Td pair is available.
- **Mixture models with boosting** (Jobst et al. 2024, arXiv:2412.09583): MIXSAMOS-GB — mixture regression on *standardised anomalies* with non-cyclic gradient boosting for automatic variable selection, reported to substantially outperform state-of-the-art post-processing for German 2 m temperature. Notable because it is a **pooled, tree-boosted, non-deep-learning** method — it combines SAMOS pooling with boosting and stays within reach of 12 CPU cores.
- **Lead-time-continuous models** (Wessel et al. 2024, doi:10.1002/qj.4701): one model across lead times instead of one per lead time — a direct answer to the parameter-count explosion of per-lead-time fitting.

**Distribution-free calibration you should know about.** Isotonic distributional regression (Henzi et al. 2021, doi:10.1111/rssb.12450) and its packaged form **EasyUQ** (Walz et al. 2024, doi:10.1137/22M1541915) convert a *single-valued* forecast into a calibrated predictive distribution using only past forecast–observation pairs, with essentially no tuning and no distributional assumption. **This is the natural first baseline for a deterministic AI model** and it is nearly free to run.

**The benchmark dataset.** EUPPBench (Demaeyer et al. 2023, doi:10.5194/essd-15-2635-2023) — time-aligned ECMWF ensemble forecasts and station observations, publicly available, with a published 2 m temperature baseline suite. **The user should fit their pipeline on EUPPBench first**, reproduce a published number, and only then point it at their own ISD-Lite/AIFS archive. It converts "is my code right?" from an unanswerable question into a checkable one.

---

## 3. Multi-station design — the user's central decision

This is the least-covered and most decision-relevant part of the literature. Four distinct strategies exist:

**(1) Local (per-station) fitting.** One model per station. Maximum site specificity, no transfer, fails on short records, and gives you 144 independent models to maintain. In Rasp & Lerch, local EMOS scored 0.90 and did not improve at all with nine years of data instead of one — it saturates.

**(2) Global/regional fitting.** One model for all stations, no site information. Robust but poor: EMOS-gl scored 1.00–1.01 versus 0.90 for local. Pooling without site information throws away exactly the representativeness signal the user has measured (station-minus-model elevation spanning −128 to +72 m).

**(3) Semi-local fitting** — Lerch & Baran 2017, *JRSS-C* (doi:10.1111/rssc.12153). **This is the paper that most directly answers the user's question.** Augment each station's training data with forecast cases from *similar* stations, where similarity is defined either by a distance function or by clustering on features of the station's climatology, its forecast errors, its ensemble predictions, and its location. Reported to significantly outperform both standard regional and standard local estimation, to allow fitting complex models without numerical instability, and to be *computationally cheaper* than local estimation. For 144 stations of uneven record length, this is the correct default: it is the principled interpolation between (1) and (2), it directly addresses short-record stations, and it needs no GPU.

**(4) Pooled fitting with learned site representation** — the Rasp & Lerch station-embedding route (doi:10.1175/MWR-D-18-0187.1). One network, station identity as a learned vector. Best performance in that study, but note the structural limitation: **an embedding is indexed by station ID, so it cannot be evaluated at a station the model never saw.** The SAMOS route (doi:10.1002/qj.2975) achieves pooling differently — by standardising away the site effect using a climatology rather than learning it — and does generalise to new sites wherever a climatology can be computed.

**Sharing information spatially rather than by identity:**

- **Graph neural networks** (Feik et al. 2024, arXiv:2407.11050): stations are nodes on a graph; an attention mechanism selects relevant predictive information from *neighbouring* stations. Case study on 2 m temperature over Europe, reporting substantial improvement over a strong DRN baseline. This is the natural architecture for a 144-station network — and note that neighbour information is a partial substitute for the observations the user does not have (e.g. it can propagate information into sparse sub-regions).
- **Area-covering EMOS** (Friedli et al. 2019, arXiv:1912.11827): replace station identity with topographical and seasonal predictors, so the model is defined everywhere rather than at station indices.
- **Clustering-based interpolation of EMOS parameters** (Baran & Baran 2024, doi:10.1175/WAF-D-24-0016.1): extend fitted predictive distributions from observation stations to *any* location in the domain, reported superior to regionally-estimated and interpolated EMOS. The route to a gridded product once station models exist.

**Generalising to stations never seen in training** — the strongest recent result:

- **convCNP downscaling** (Vaughan et al. 2022, arXiv:2101.07950): a convolutional conditional neural process for multisite downscaling of temperature and precipitation. The architectural point is decisive — **the trained model can generate predictions at an arbitrary set of locations regardless of the availability of training data there**, because it maps a gridded field plus a location to a distribution, rather than looking up a station index.
- **Earth-observation embeddings as sub-grid descriptors** (Sousa et al. 2026, arXiv:2608.12271). The most directly relevant recent paper for the representativeness problem. A convCNP downscaling ~25 km ERA5 is augmented with a learned local surface descriptor built by compressing 10 m TESSERA embeddings, replacing hand-crafted topographic descriptors. Across five climatically diverse regions this improved **CRPS skill by 11.5% for 2 m temperature and 6.2% for 10 m wind at stations held out in both space and time**, with the improvement persisting when the coarse input was switched from ERA5 to **Aurora AI-model forecasts**, and at newly deployed stations with no regional history. Two things to take from it: learned surface embeddings can stand in for the topographic descriptors the user would otherwise hand-build, and **the "held out in space" evaluation protocol is the one the user should adopt.**
- **Terrain-descriptor construction** (Winstral et al. 2017, doi:10.1175/JHM-D-16-0054.1) is the reference for building local topography predictors by hand — the baseline the embedding papers are trying to beat.

---

## 4. AI forecast models and their post-processing

This is where the user's project is actually located, and the literature is thin enough that a careful study has room to contribute.

**The forecast source.** AIFS-CRPS (Lang et al., *npj Artificial Intelligence*, doi:10.1038/s44387-026-00073-7) — ECMWF's AI ensemble trained directly on the almost-fair CRPS, which approximately removes finite-ensemble-size bias in the score. It is stochastic and can emit arbitrarily many exchangeable members, and **for medium-range forecasts it outperforms the IFS ensemble for the majority of variables and lead times**. Two consequences for the user: (a) the members are *exchangeable*, so member-identity methods (BMA weights, member-by-member) are pointless — use mean and spread, or a permutation-invariant treatment; (b) the model is already CRPS-trained, so it may be better calibrated *a priori* than IFS ENS, and the raw-ensemble baseline is correspondingly harder to beat. Ben Bouallègue et al. 2024 (doi:10.1175/BAMS-D-23-0162.1) is the systematic assessment of where AI models win and where they are over-smooth or biased.

**The single most relevant paper in this whole review** is Trotta et al. 2025, *AIES* (doi:10.1175/AIES-D-25-0037.1). The Australian Bureau of Meteorology took its **existing operational post-processing system (IMPROVER) and applied it unmodified to deterministic AIFS**, comparing against post-processed ECMWF HRES and ENS, verified against quality-controlled observations at **569 automatic weather stations**. Findings, in the authors' framing: post-processing yields *comparable* accuracy improvements for AIFS as for traditional NWP, in both expected value and probabilistic output, with no workflow changes; and **blending AIFS with NWP models improves overall skill even when AIFS alone is not the most accurate component**. For temperature and dew point, AIFS was generally the main blend component early in the forecast period; a blend of ENS+AIFS achieved accuracy very similar to the all-model blend. The strategic implication for the user is direct and encouraging: **methods developed for IFS transfer to AIFS essentially as-is** — so the classical EMOS literature above is not wasted effort — **and combining AIFS with IFS ENS is likely to beat either alone.** Both archives are available to them at 0.25°.

**Uncertainty quantification for deterministic AI models.** Bülte et al. (doi:10.1175/AIES-D-24-0049.1; preprint arXiv:2403.13458) systematically compare routes to probabilistic forecasts from deterministic Pangu-Weather: initial-condition perturbation ensembles versus statistical and ML post-hoc UQ. Over Europe at medium range they report the resulting probabilistic forecasts improving on the physics-based ECMWF ensemble **for lead times up to 5 days**. Relevant if the user ever wants to use a deterministic AI model rather than AIFS ENS.

**How to compare fairly.** Gneiting et al. 2025 (arXiv:2506.03744) introduce the **potential CRPS (PC)**: subject the deterministic backbone of *both* the AI and the physical model to the same statistical post-processing (IDR), then compare mean CRPS. This is the methodologically correct way to ask "is AIFS better than IFS over NW Russia" — because otherwise you are partly measuring which model happens to be better calibrated out of the box, not which carries more information.

---

## 5. Reading order

1. **Vannitsem et al. 2021** (doi:10.1175/BAMS-D-19-0308.1) — the field review. Read for the map, not the details.
2. **Taillardat et al. 2016** (doi:10.1175/MWR-D-15-0260.1) — QRF; the cleanest statement of the non-parametric alternative, and readable.
3. **Gneiting et al. 2005** (doi:10.1175/MWR2904.1) — EMOS. Short, and you need the variance link in your head.
4. **Rasp & Lerch 2018** (doi:10.1175/MWR-D-18-0187.1) — the anchor. Read Table 2 line by line.
5. **Schulz & Lerch 2022** (doi:10.1175/MWR-D-21-0150.1) — the eight-method comparison; copy the experimental design.
6. **Lerch & Baran 2017** (doi:10.1111/rssc.12153) — semi-local estimation; your per-station-vs-pooled decision.
7. **Trotta et al. 2025** (doi:10.1175/AIES-D-25-0037.1) — post-processing applied to AIFS at 569 stations. Your project's closest precedent.
8. **Demaeyer et al. 2023** (doi:10.5194/essd-15-2635-2023) — EUPPBench; fit your pipeline here first.
9. **Sousa et al. 2026** (arXiv:2608.12271) — learned surface descriptors, held-out-in-space evaluation.
10. **Walz et al. 2024** (doi:10.1137/22M1541915) — EasyUQ; the cheapest possible baseline.
11. **Dabernig et al. 2017** (doi:10.1002/qj.2975) — SAMOS; the pooling trick that needs no deep learning.
12. **Jobst et al. 2024** (arXiv:2412.09583) — MIXSAMOS-GB; where pooling + boosting currently sits for German 2 m temperature.

---

## 6. Practical implications for this project

- **The 3% rule.** Budget for ML beating a *well-tuned* classical baseline by single-digit percent. Design the study so a 3% result is publishable — which means the baseline must be boosted EMOS or SAMOS, not raw ensemble and not global EMOS. A paper that only reports "29% over raw" is not making a contribution any more.
- **Fit boosted EMOS (doi:10.1175/MWR-D-16-0088.1) and EasyUQ (doi:10.1137/22M1541915) before any neural network.** Both are cheap, both are strong, and the second one requires almost no tuning.
- **Semi-local or SAMOS pooling, not per-station fitting.** With 144 stations of uneven length, per-station EMOS saturates (Rasp & Lerch: 0.90 → 0.90 with 9× the data) and QRF is data-starved (0.95 → 0.81). Pooling is where the leverage is.
- **Use station embeddings only if you never need unseen stations.** If generalisation matters — and for a sparse domain with 15 stations sitting on ERA5 water cells it probably does — use terrain/land-surface predictors (arXiv:1912.11827) or a location-conditioned architecture (arXiv:2101.07950) instead of an ID-indexed embedding.
- **Everything is a temperature model until proven otherwise.** The ISD-Lite precipitation gap is not a limitation on this literature: temperature is where the field's reference results are, and it is the right first variable.
- **Exploit the dew point.** It is ~99–100% complete in the archive, and the physics-constrained approach (doi:10.1175/AIES-D-22-0089.1) turns the T/Td pair into a consistency constraint that helps most when data are scarce.
- **Verification discipline.** Sharpness subject to calibration (doi:10.1111/j.1467-9868.2007.00587.x); CRPS plus PIT/rank histograms; and account for temporal autocorrelation of station errors (doi:10.1002/qj.3667) before claiming significance. Use Diebold–Mariano tests with a multiple-testing correction across stations, as Rasp & Lerch do.
- **Blend AIFS ENS with IFS ENS.** Trotta et al. found the blend beat either component even when AIFS alone was not the most accurate (doi:10.1175/AIES-D-25-0037.1), and both archives are available to the user at 0.25°. Multi-model EMOS is the classical machinery for this (arXiv:2008.07857).
- **Expect winter and coast to be the hard cases.** Keller et al. report all forecast variants performing worst in DJF (arXiv:2008.07857); Alerskans et al. report degradation with proximity to coast and in cold temperatures (doi:10.1002/met.2098). A Baltic-to-White-Sea domain with a continental winter has both problems at once, which makes them the interesting part of the result rather than a caveat.

---

## 7. Research gaps a NW-Russia AIFS project could occupy

Each of these is a gap I can evidence from what the retrieved literature does and does not contain — not a wish list.

1. **AI-ensemble post-processing has been demonstrated at station level in essentially one place.** Trotta et al. (doi:10.1175/AIES-D-25-0037.1) is Australia, 569 AWS, and uses *deterministic* AIFS inside an operational framework. Post-processing **AIFS-CRPS ensemble** output to stations, in a high-latitude continental/maritime European domain, with an open-data-only pipeline, is not covered. This is the clearest opening.
2. **High-latitude and Russian domains are absent.** Every station-level benchmark retrieved here is Germany (175–1000+ stations), Switzerland, Denmark, France, Hungary, Europe-wide EUPPBench, or Australia. Nothing covers 55–70.5 N in European Russia. Snow-covered surfaces, strong winter inversions, polar night, and freeze-up/break-up of the White Sea are conditions under which the EMOS variance link and Gaussian assumption are least likely to hold — and under which every retrieved paper reports its worst scores.
3. **Winter inversions are named as the failure mode but not attacked.** Papers consistently report DJF as worst (arXiv:2008.07857) and cold temperatures as degrading (doi:10.1002/met.2098), yet I found no station post-processing study whose *design* targets strong stable boundary layers — e.g. conditioning the predictive distribution on inversion strength or snow cover, or allowing a bimodal predictive distribution for inversion-breakup timing. Mixture models (arXiv:2412.09583) exist but are not applied to this.
4. **Representativeness error is corrected implicitly, never modelled.** The literature handles station-minus-model mismatch either by learning an ID-indexed embedding (doi:10.1175/MWR-D-18-0187.1), by standardising it away (doi:10.1002/qj.2975), or by hand-built terrain descriptors (doi:10.1175/JHM-D-16-0054.1). The user has *measured* the mismatch — elevation offsets of −128 to +72 m, σ ≈ 29 m, and 15 of 144 stations on cells the model calls water. **Treating elevation offset and land/water misclassification as explicit, physically-interpretable predictors and reporting skill stratified by them is a concrete, small, publishable contribution** that the retrieved literature leaves open. The land/water-misclassification case in particular appears in no retrieved paper.
5. **Sub-daily-frequency heterogeneity is unaddressed.** Every benchmark I retrieved uses a homogeneous observation network (hourly, or a single reporting cadence). The user's network is mixed hourly and 3-hourly with varying record lengths. How to pool across stations with *different sampling frequencies* — rather than different record lengths, which Lerch & Baran do address (doi:10.1111/rssc.12153) — is not covered.
6. **Held-out-in-space evaluation is rare.** Only the convCNP line (arXiv:2101.07950, arXiv:2608.12271) and the parameter-interpolation work (doi:10.1175/WAF-D-24-0016.1) genuinely test at unseen locations. Most station studies report held-out-in-time only. A study that reports both, on a sparse network, would be unusually informative — and it is a design choice that costs nothing but discipline.
7. **The compute-constrained regime is undocumented.** The methods that win in the literature are reported from institutional settings. Nothing retrieved here asks: *what is the best achievable station-level skill on 12 CPU cores and a 4 GB GPU with open data only?* Given the 3%-over-classical reality, the answer may be "almost all of it" — and that is a genuinely useful, honestly-motivated result for the large community of researchers without institutional access.
8. **AIFS-vs-IFS comparison at station level lacks the fair-comparison treatment.** The PC-score framework (arXiv:2506.03744) exists precisely to separate "better information" from "better calibration", and has not been applied to station-level verification in a high-latitude domain. Applying it would make the user's headline claim defensible rather than arguable.

---

## 8. Coverage caveats

- **The strongest quantitative benchmark in the ML literature is for wind gusts, not temperature.** Schulz & Lerch 2022 (doi:10.1175/MWR-D-21-0150.1) is the eight-method comparison, and its magnitudes should not be transferred to 2 m temperature. Rasp & Lerch remains the best-quantified temperature comparison, and it is a 2018 paper using a 2007–2016 archive.
- **Percentages across papers are not comparable.** 29% (Rasp & Lerch, German stations, ECMWF ENS, 1-yr training), 16.5% (Van Poecke, EUPPBench, 20 lead times), 30% (Keller, Swiss stations, vs high-res *deterministic* output), 11.5% (Sousa, five regions, downscaling ERA5, held out in space) all measure different things against different baselines. I have kept the baseline attached to every number above for this reason.
- **Several key items are preprints** (arXiv:2608.12271, arXiv:2407.11050, arXiv:2412.09583, arXiv:2506.03744) and are flagged as such in the citation table. The 2026 EO-embedding paper in particular is very recent and unreplicated.
- **Search returned little on two topics I looked for specifically.** (a) Post-processing with *explicit* representativeness-error models — as opposed to embeddings or terrain proxies — returned nothing usable; this supports gap 4 but I cannot rule out that the relevant work exists under vocabulary I did not try. (b) Graph-neural-network post-processing is represented by one preprint (arXiv:2407.11050); repeated searches for published GNN post-processing work returned off-topic results, so this line appears genuinely young rather than under-retrieved.
- **Language coverage.** Searches were English-language via OpenAlex and arXiv. Russian-language work on statistical correction of NWP over this exact domain (Roshydromet, Hydrometeorological Research Centre of Russia) would not appear and may well exist. The user may be better placed than these databases to find it — and it would be worth checking before claiming domain novelty.
- **Precipitation was deliberately not surveyed in depth**, consistent with the project's ISD-Lite constraint. The relevant entry points if that changes are doi:10.1002/wat2.1246 and doi:10.1175/WAF-D-18-0149.1.
