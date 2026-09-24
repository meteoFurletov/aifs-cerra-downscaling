# Forecast verification for a station-level AIFS downscaling project

*Literature review, verification track. All citations below were retrieved from OpenAlex or arXiv
during this review; author names, years and venues come from the retrieved records, not from recall.
Preprints are labelled. 78 papers retrieved and catalogued in `cites_verification.csv`.*

---

## What I searched, and what came back thin

I ran roughly sixty OpenAlex queries and a dozen arXiv queries across four rounds, then walked the
citation graph backward (references) and forward (citations) from six anchor papers: the ensemble-size
convergence paper, the finite-ensemble score paper, the operational AI assessment, the neighbourhood
verification paper, a downscaling intercomparison, and the calibration-and-sharpness paper. The graph
walk earned its keep — the primary fair-scores paper did not surface from any keyword query I tried
and only appeared as a forward citation.

Three sub-areas came back genuinely thin, and I am reporting that rather than padding:

1. **Verification protocol specifically for station-level post-processing of AI ensemble forecasts.**
   This barely exists. There is protocol literature for post-processing generally, and there is
   evaluation literature for AI models on grids, but the intersection — how you should cross-validate
   a model that maps AI ensemble output to 144 irregularly spaced stations — is not written down.
   Queries on station-versus-analysis post-processing and on leave-one-station-out designs returned
   mostly off-topic results. This is a real gap and it is one your project sits directly inside.
2. **Autocorrelation-aware confidence intervals for verification scores.** I found the general
   statistical machinery (block bootstrap, Diebold–Mariano) and I found meteorological papers that
   invoke it, but I found no paper that systematically works out effective sample size for
   multi-station, multi-lead-time score differences. Practitioners appear to improvise.
3. **Persistence as a baseline in probabilistic post-processing.** The hydrology literature is
   explicit about baseline hierarchies; the NWP post-processing literature mostly is not, and my
   queries for persistence baselines returned little of substance.

---

## Question 1: What makes a score legitimate at all?

The single most important idea in this literature is that most obvious-looking accuracy measures are
not merely imprecise but actively *corruptible* — they can be improved by reporting something other
than your honest belief. A scoring rule is **proper** if your expected score is optimised by issuing
your true predictive distribution, and **strictly proper** if that optimum is unique. Everything else
in verification is downstream of this property. The foundational treatment is
[Gneiting and Raftery 2007](https://doi.org/10.1198/016214506000001437), which defines propriety, situates the
continuous ranked probability score (CRPS), the logarithmic score and the energy score inside a single
framework, and shows how each arises from a convex-function construction. Its meteorological
companion, [Bröcker and Smith 2007](https://doi.org/10.1175/waf966.1), makes the practical argument in the
language a forecaster uses: with an improper score you can gain by *hedging*, i.e. by shifting your
stated probabilities away from your beliefs toward whatever the score rewards. If you optimise an
improper score you are training your model to lie, and it will.

The same logic constrains deterministic verification, which is where most people get caught.
[Gneiting 2011](https://doi.org/10.1198/jasa.2011.r10138) shows that a point forecast is only meaningful relative
to a *pre-declared functional* of the predictive distribution, because each scoring function is
consistent for a specific functional: squared error elicits the mean, absolute error elicits the
median, and the pinball loss elicits a quantile. "Should I report RMSE or MAE?" is therefore not a
free stylistic choice — it silently decides what the model is being asked to predict. Announce the
functional first, then pick the score that is consistent for it. This matters enormously for your
project because it dictates that if you evaluate with RMSE, you have asked for the conditional mean,
and a conditional mean is a smooth object.

Beyond propriety, [Murphy 1993](https://doi.org/10.1175/1520-0434(1993)008%3C0281:wiagfa%3E2.0.co;2) supplies
the framing that keeps a verification study honest: forecast goodness has three distinct types —
*consistency* (does the forecast match the forecaster's judgement), *quality* (does it match
observations), and *value* (does it help a user decide). A single scalar cannot express all three, so
any credible evaluation reports several complementary diagnostics rather than one headline number.
For orientation across the whole field, [Gneiting and Katzfuss 2014](https://doi.org/10.1146/annurev-statistics-062713-085831)
is the review to read, and [Jordan, Krüger and Lerch 2019](https://doi.org/10.18637/jss.v090.i12) is the reference
software implementation — you should compute CRPS with `scoringRules` (or a port of it) rather than
hand-rolling an estimator, for reasons that Question 4 makes concrete.

## Question 2: What is a probabilistic forecast actually trying to achieve?

The organising principle of modern probabilistic forecasting is a constrained optimisation, and it is
worth stating in one sentence because it determines the whole shape of an evaluation:
**maximise sharpness subject to calibration.** This is the thesis of
[Gneiting, Balabdaoui and Raftery 2007](https://doi.org/10.1111/j.1467-9868.2007.00587.x), and its force lies in
the asymmetry between the two terms. Calibration is a joint property of forecasts and observations —
it is a constraint you must satisfy, and a forecast that fails it is wrong, not merely imprecise.
Sharpness is a property of the forecasts alone — it is the objective you maximise once the constraint
holds. The paper also distinguishes several modes of calibration (probabilistic, exceedance,
marginal), which matters because a forecast can be marginally calibrated over a whole sample while
being badly miscalibrated in every individual regime.

The practical consequence is that any proper score is implicitly a sum of a calibration term and a
sharpness term, and that the two must be reported separately as well as jointly. A single CRPS number
tells you which system is better overall; it does not tell you whether the loser is unreliable or
merely vague, and those two diseases have entirely different cures. In a post-processing project the
distinction is the whole game: statistical post-processing chiefly repairs calibration, and its
ability to add sharpness is limited by the information content of the raw forecast.

## Question 3: What does each standard diagnostic actually diagnose?

The diagnostics form a division of labour, and using the wrong one is the most common failure in
amateur verification work. The following is what each one is *for*.

**CRPS and its decomposition.** [Hersbach 2000](https://doi.org/10.1175/1520-0434(2000)015%3C0559:dotcrp%3E2.0.co;2)
splits the mean CRPS of an ensemble system into a **reliability** part and a **potential CRPS** — the
score the system would attain if it were perfectly reliable, i.e. the part attributable to genuine
resolution and sharpness rather than to miscalibration. This is the single most useful diagnostic
decomposition for your purposes, because it separates "my post-processing fixed the calibration" from
"my post-processing added information". Post-processing that drives reliability to zero while leaving
potential CRPS untouched has fixed the spread, not improved the forecast. Be aware that the classical
binned decomposition is itself biased at finite sample and ensemble size;
[Arnold, Lerch, Dimitriadis and Gneiting 2024](https://doi.org/10.1214/24-ejs2316) gives the modern rigorous
treatment and the bias-corrected alternatives.

**Rank histograms.** [Hamill 2001](https://doi.org/10.1175/1520-0493(2001)129%3C0550:iorhfv%3E2.0.co;2) is
the paper to read, and its value is mostly cautionary: a U-shaped rank histogram is *conventionally*
read as underdispersion, but Hamill demonstrates that conditional bias, non-stationary variance and
correlated errors produce the same shapes without any true underdispersion. A rank histogram is a
necessary-but-not-sufficient check, and it is not a score.
[Marzban, Wang, Kong and Leyton 2010](https://doi.org/10.1175/2010mwr3129.1) sharpens the warning specifically
for the case that applies to you: when verification samples are spatially or temporally correlated —
which is exactly what pooling 144 stations across a synoptic-scale domain does — the histogram is
distorted even for a perfectly calibrated system. If you pool your stations into one rank histogram,
you will see a U-shape you did not earn.

**Reliability diagrams.** The classical binned-and-counted reliability diagram is unstable under
arbitrary binning choices, a problem which was tolerated for decades. It now has a clean solution:
the **CORP** approach of [Dimitriadis, Gneiting and Jordan 2021](https://doi.org/10.1073/pnas.2016191118) uses
isotonic regression (the pool-adjacent-violators algorithm) instead of binning, which is provably
optimal, reproducible, and carries a consistent score decomposition into miscalibration,
discrimination and uncertainty components plus uncertainty bands. Use this rather than binned plots;
there is no longer a reason not to. The theoretical framing is developed further in
[Gneiting and Resin 2023](https://doi.org/10.1214/23-ejs2180), which recasts conditional calibration assessment
as regression diagnostics, and [Dimitriadis, Gneiting, Jordan and Vogel 2023](https://arxiv.org/abs/2301.10803)
(preprint) proposes the "triptych" — reliability, discrimination and a Murphy diagram side by side —
as a standard joint display. For multicategory forecasts the older treatment in
[Hamill 1997](https://doi.org/10.1175/1520-0434(1997)012%3C0736:rdfmpf%3E2.0.co;2) still frames the problem.

**Spread–skill relationships.** [Whitaker and Loughe 1998](https://doi.org/10.1175/1520-0493(1998)126%3C3292:trbesa%3E2.0.co;2)
established the original relationship and its central caveat: ensemble spread predicts ensemble-mean
error only in a distributional sense, not case by case, and the strength of the relationship depends
on the variability of the spread itself. There is then a specific, widely-botched technical point that
you must get right. [Fortin, Abaza, Anctil and Turcotte 2014](https://doi.org/10.1175/jhm-d-14-0008.1) show that
for an *M*-member ensemble the spread should not be compared to the RMSE of the ensemble mean
one-to-one; the correct target ratio carries a factor of √((M+1)/M). Comparing to 1.0 makes every
finite ensemble look underspread. At M = 51 the factor is about 1.0097, so the error is small but not
zero; if you subsample to 10 members it is about 1.049, and at 5 members about 1.095 — at which point
"my ensemble is underdispersed" may be entirely an artefact of your arithmetic.
[Dirkson, Merryfield and Monahan 2025](https://doi.org/10.1175/mwr-d-24-0189.1) revisits the same problem for MSE
and the spread–error relationship with correction factors.

**Observation error.** Before you declare an ensemble underdispersed you must account for the error in
the verifying observation, because observation error inflates the apparent error of the forecast
without inflating the spread. [Sætra, Hersbach, Bidlot and Richardson 2004](https://doi.org/10.1175/1520-0493(2004)132%3C1487:eooeot%3E2.0.co;2)
work this through for ensemble spread and reliability statistics and show how to add observation-error
variance to the spread before comparison. [Candille and Talagrand 2005](https://doi.org/10.1256/qj.04.71) build a
systematic framework for scalar probabilistic evaluation that carries observation error through
reliability and resolution. For general interpretation of summary ensemble measures,
[Bradley, Schwartz and Demargne 2011](https://doi.org/10.1175/2010mwr3305.1) and
[Mason 2008](https://doi.org/10.1002/met.51) are useful practitioner-level companions.

## Question 4: Fair versus unfair CRPS — and why it is worth 2% to you

This is the most immediately actionable item in the whole review, so I quantified it rather than
merely citing it.

The standard sample estimator of the ensemble CRPS is biased for finite ensembles: it penalises an
ensemble drawn from the *correct* predictive distribution simply for being finite. The reason is
structural — the estimator's second term measures the internal spread of the ensemble using a
normalisation that treats the ensemble as if it were the population, so a finite sample looks
insufficiently spread relative to the truth. [Ferro, Richardson and Weigel 2008](https://doi.org/10.1002/met.45)
first quantified this effect for the discrete and continuous ranked probability scores and gave the
correction. [Ferro 2013](https://doi.org/10.1002/qj.2270) then generalised it into the concept of a **fair score**:
a score which, in expectation, is optimised by an ensemble whose members are drawn from the true
distribution, independently of how many members there are. The distinction is not cosmetic. An unfair
score rewards a system for having more members; a fair score rewards it only for being right.

I derived and verified the magnitude. For an ensemble of *M* members drawn from the true predictive
distribution, the expected standard ("unfair") CRPS exceeds the population value by a factor of
exactly (1 + 1/*M*), so the relative inflation is exactly **1/*M***, independent of the distribution.
A Monte Carlo experiment over calibrated Gaussian ensembles confirms this to within Monte Carlo error
at every size tested (M = 2 gives 50.10% ± 0.06 against an exact 50%; M = 51 gives 1.88% ± 0.12
against an exact 1.96%), and confirms the fair estimator is unbiased at all sizes.

![Standard CRPS inflation as a function of ensemble size. Left: the relative penalty applied to a perfectly calibrated ensemble is exactly 1/M — 2.0% at the 51 members of AIFS ENS, 10% at a 10-member subsample. Shaded band marks the ~2% scale of post-processing gains this project has previously measured. Right: expected score for the two estimators; only the fair CRPS is comparable across ensemble sizes.]({{artifact:art_446aa4aa-0911-430e-9942-068e2dc138e1}})

Read the left panel against your own numbers. Earlier work in this project found that the best
correction method beat ERA5 by **+2.2%**, and that two other methods came in *negative*. The
finite-ensemble artefact at 51 members is **1.96%**. In other words, the bookkeeping error you would
commit by using the wrong CRPS estimator is the same size as the entire effect you are trying to
measure. If you ever compare configurations with different member counts — the 51-member ENS against a
subsample, or against a lagged ensemble, or against a parametric post-processed distribution that
effectively has infinite members — an unfair score will hand victory to whichever has more members,
regardless of merit.

The supporting literature completes the picture. [Zamo and Naveau 2017](https://doi.org/10.1007/s11004-017-9709-7)
compare CRPS estimators from limited ensembles and warn specifically against comparing a parametric
predictive distribution with an ensemble without accounting for the estimator difference — which is
precisely the comparison a post-processing study makes when it pits a fitted Gaussian against the raw
ensemble. [Ferro and Fricker 2012](https://doi.org/10.1002/qj.1924) give the analogous bias-corrected
decomposition of the Brier score. [Leutbecher 2018](https://doi.org/10.1002/qj.3387) settles the practical
question of how many members you need, using a 200-member IFS experiment to trace the convergence of
CRPS, quantile score and Dawid–Sebastiani score with ensemble size, and finds the fair versions
converge far faster — the paper's title, "how suboptimal is less than infinity?", is the question you
should be asking about your own subsampling choices.
[Leutbecher and Ben Bouallègue 2019](https://doi.org/10.1002/qj.3704) apply fair scores to compare dual-resolution
configurations with unequal member counts, which is the methodological template for any comparison you
make across ensemble sizes. The older [Buizza and Palmer 1998](https://doi.org/10.1175/1520-0493(1998)126%3C2503:ioesoe%3E2.0.co;2)
gives the classic demonstration that skill saturates with ensemble size.

Finally, and directly about your model: [Lang et al. 2024](https://arxiv.org/abs/2412.15832) (preprint) documents
**AIFS-CRPS**, ECMWF's ensemble AIFS trained on an *almost-fair* CRPS. The relevant detail for you is
*why* "almost": the strictly fair CRPS degenerates when used as a training loss — optimising it
directly permits pathological solutions — so they interpolate between the fair and unfair forms with a
small weighting. This is a valuable piece of information about your intended input, because it means
the AIFS ENS you download was itself trained against a specific finite-ensemble-aware objective, and
your evaluation should be aware of the same subtleties as its training.

## Question 5: Why RMSE rewards smoothing, and why this defeats the purpose of downscaling

This is the trap that most threatens your project, and it follows directly from Question 1. If squared
error is consistent for the conditional mean, then the RMSE-optimal single field *is* the conditional
mean — a smooth, low-variance field. Minimising RMSE therefore does not ask a model to be realistic;
it asks it to be cautious. A model that damps its own small scales loses little in RMSE and gains
protection against being confidently wrong. This is not a subtle statistical curiosity, it is the
dominant behaviour of current AI weather models, and it is precisely the property that a downscaling
project is supposed to remove.

The clearest statement of the diagnosis is [Bonavita 2024](https://doi.org/10.1029/2023gl107377), which uses
spectral analysis to show that leading data-driven models systematically deficit energy at small
scales, so that their *effective* resolution is substantially coarser than their nominal grid spacing,
and the damping worsens with lead time. A nominally 0.25° field can therefore be considerably blurrier
than 0.25°. If you feed such a field into a downscaling scheme and evaluate the result with RMSE, you
will find that the scheme's best strategy is to stay blurry.

[Rasp et al. 2024](https://doi.org/10.1029/2023ms004019) — WeatherBench 2 — is the paper that makes this concrete
as an evaluation problem rather than a modelling problem. It establishes the reference protocol for
data-driven models, and it discusses explicitly how blurring lowers RMSE while a categorical
precipitation score reverses the resulting model ranking. That reversal is the single most useful
empirical fact in this section: the same two models can be ordered oppositely by an averaging score
and a categorical score, and only one of those orderings reflects physical realism. The categorical
score in question, **SEEPS**, comes from [Rodwell, Richardson, Hewson and Haiden 2010](https://doi.org/10.1002/qj.656),
and it was designed for exactly this purpose — an equitable score for precipitation constructed so
that hedging toward the climatologically safe category does not pay.

Two further papers extend the argument to the probabilistic case, which is where you will live.
[Ben Bouallègue et al. 2024](https://doi.org/10.1175/bams-d-23-0162.1) provides the first operational-style
statistical assessment of a machine-learning model against the IFS, verified against both analyses and
synoptic observations, and identifies over-smoothing as a core drawback of the AI forecast despite
competitive headline scores. [Brenowitz et al. 2025](https://doi.org/10.1029/2024gl113656) constructs a practical
probabilistic benchmark using lagged ensembles and shows that the deterministic skill ranking of AI
models does *not* carry over to probabilistic skill — a model that wins on RMSE can lose on CRPS. The
mechanism by which training choices destroy small scales is illustrated in
[Smith et al. 2023](https://doi.org/10.1029/2023ms003792), which shows temporal subsampling in recurrent
emulators diminishing small spatial scales.

There is an older and directly analogous literature in statistical downscaling that you should not
skip, because it made the same mistake first and diagnosed it thoroughly.
[Gutiérrez et al. 2012](https://doi.org/10.1175/jcli-d-11-00687.1) show that naive distribution mapping distorts
variance and inflates trends, and the standard reference text,
[Maraun and Widmann 2017](https://doi.org/10.1017/9781107588783), treats the variance-inflation problem and the
validation of downscaling methods at book length. The general lesson transfers exactly: any method
that adjusts marginals without respecting the underlying physical variability will produce fields that
score well and are wrong.

**The protocol implication is unavoidable: you cannot use RMSE, or CRPS alone, as your only headline
metric.** You need at least one diagnostic that is sensitive to variance and small-scale structure —
a spectral comparison, a variance ratio, or a categorical/threshold score — reported alongside the
averaging score, every time. Otherwise your evaluation will actively reward the failure mode you set
out to fix.

## Question 6: The double penalty and spatial verification — how much of this applies to you?

The double-penalty problem is the grid-based cousin of the smoothing trap. A high-resolution forecast
that predicts a feature with the right intensity but a small displacement is penalised twice by any
grid-point-wise score — once for predicting the feature where it is not, and once for failing to
predict it where it is. A blurred forecast avoids both penalties. The result is that grid-point
verification systematically prefers the lower-resolution forecast, and the field's response was to
build scores that verify at a scale rather than at a point.

The canonical answer is the **Fractions Skill Score** of
[Roberts and Lean 2008](https://doi.org/10.1175/2007mwr2123.1), which compares forecast and observed exceedance
*fractions* within neighbourhoods of increasing size and identifies the **skilful scale** — the
neighbourhood size at which the forecast becomes useful. This reframes the question from "is it right
here?" to "at what scale is it right?", which is the correct question for high-resolution output.
[Roberts 2008](https://doi.org/10.1002/met.57) extends this to how skilful scale varies in space and time, and
[Mittermaier and Roberts 2011](https://doi.org/10.1002/met.296) gives a long-term operational assessment with
practical guidance on neighbourhood sizes. The wider family of neighbourhood ("fuzzy") methods is
systematised in [Ebert 2008](https://doi.org/10.1002/met.25), and the field's own intercomparison of the competing
approaches — neighbourhood, scale-separation, features-based, field-deformation — is
[Gilleland et al. 2009](https://doi.org/10.1175/2009waf2222269.1), the overview paper of the Spatial Verification
Method Intercomparison Project. For alternatives to neighbourhoods, the features-based SAL score has
an ensemble version in [Radanovics, Vidal and Sauquet 2018](https://doi.org/10.1175/waf-d-17-0162.1), and
[Dey et al. 2016](https://doi.org/10.1002/qj.2792) reframes the same problem as one of local spatial
predictability. [Casati et al. 2008](https://doi.org/10.1002/met.52) and
[Casati et al. 2022](https://doi.org/10.1175/bams-d-21-0126.1) bracket the sub-field's development and current
state.

Two of these have specific bearing on your situation. First, if you use FSS on an *ensemble* you must
be careful which formulation you pick: [Necker et al. 2024](https://doi.org/10.1002/qj.4824) show that four
plausible ensemble generalisations of FSS behave very differently, and only the probabilistic
formulation is well behaved as ensemble size changes — the same finite-ensemble theme as Question 4,
resurfacing in a spatial score. Second, verification of *wind* in orographically complex terrain using
neighbourhoods has a direct template in [Skok and Hladnik 2017](https://doi.org/10.1175/mwr-d-16-0471.1), which is
relevant given the elevation-mismatch problem already measured in your station set.

**An honest caveat about applicability.** Most of this literature assumes a gridded observational
analysis, and you have 144 point stations and no precipitation. Neighbourhood scores over a sparse
irregular point network are not the same object as neighbourhood scores over a radar grid, and the
skilful-scale concept partly loses its meaning when observations are 50–200 km apart. You should read
this literature to understand *why* your headline scores can mislead — the double penalty is the
mechanism behind the smoothing reward — but the spatial-score machinery itself is largely not
directly deployable on your data. The deployable version of the same insight, for you, is the
variance/spectral check recommended at the end of Question 5, plus threshold-based categorical scores
at individual stations.

## Question 7: Point observations versus gridded analyses

Verifying against station observations and verifying against a gridded analysis are different
experiments that answer different questions, and the difference is not a nuisance to be minimised —
it is structural. A grid box is an areal average; a station is a point with its own exposure,
elevation and instrument. The mismatch between them is *representativeness error*, and it does not
shrink as the model improves. [Ebert et al. 2013](https://doi.org/10.1002/met.1392) is the standard review
covering representativeness, point-versus-grid mismatch and the resulting spatial methods, and it is
the right entry point.

The practical hazards are larger than most people expect. [Accadia et al. 2003](https://doi.org/10.1175/1520-0434(2003)018%3C0918:sopfss%3E2.0.co;2)
show that the *interpolation method alone* — bilinear versus nearest-neighbour averaging — materially
changes precipitation skill scores on high-resolution verification grids. That is a result about your
methodology, not about the weather: how you get from the 0.25° AIFS grid to a station location is a
scientific choice that will show up in your numbers, and it must be fixed in advance and reported.
For station-level verification specifically, [Nurmi 1994](https://doi.org/10.21957/dx25q07hu) remains the most
directly applicable practical checklist in the literature — it is an ECMWF technical memorandum on
verifying local forecasts, and it is more useful to you than most of the recent literature.

There is also a decisive methodological point in [Ben Bouallègue et al. 2024](https://doi.org/10.1175/bams-d-23-0162.1):
they verify against both the analysis and synoptic observations, and the two verifications do not
agree. Verifying an AI model against a reanalysis flatters it, because the reanalysis and the model
share a representation of the atmosphere. Your project has already discovered the local version of
this — ERA5 assimilates the very SYNOP stations you are verifying against, so ERA5 is pinned to them
and no correction improves it. Both facts are the same fact: **shared information between your
"truth" and your forecast manufactures apparent skill.** Station observations are the right truth for
your project precisely because AIFS forecasts at +24 h and beyond have not seen them.

## Question 8: Protocol — how to split data without fooling yourself

Naive random *k*-fold cross-validation is invalid for your data, in two independent ways at once, and
this is the area where a self-taught project is most likely to produce a result that cannot be
defended.

The first leak is temporal. Weather is serially autocorrelated over days; a random split puts
2 January in training and 3 January in test, and the model is effectively told the answer. The formal
treatment is [Racine 2000](https://doi.org/10.1016/s0304-4076(00)00030-0), which introduces **hv-block**
cross-validation: hold out a contiguous block, and additionally *delete* a buffer of observations on
each side of it so that the training set contains nothing within the correlation length of the test
set. That buffer is the part everyone omits and it is the part that matters.
[Cerqueira, Torgo and Mozetič 2020](https://doi.org/10.1007/s10994-020-05910-7) compare performance-estimation
methods for time series empirically, covering blocked and forward-chaining schemes against naive
*k*-fold.

The second leak is spatial. Your 144 stations are not independent samples: neighbouring stations in a
synoptic-scale domain share weather, and a model that has memorised one station's behaviour will
appear to predict its neighbour. The reference paper is
[Roberts et al. 2016](https://doi.org/10.1111/ecog.02881), which sets out blocked cross-validation for data with
temporal, spatial, hierarchical or phylogenetic structure — it is written for ecology but it is the
clearest general treatment and is heavily cited across the geosciences. Two refinements matter.
[Schratz et al. 2019](https://doi.org/10.1016/j.ecolmodel.2019.06.002) show that hyperparameter tuning must be
*nested inside* the spatial cross-validation, not performed outside it — tuning on the same folds you
evaluate on leaks just as surely as training on them. And
[Meyer and Pebesma 2021](https://doi.org/10.1111/2041-210x.13650) provide the **area of applicability**: a method
for delineating the region of predictor space where a spatially trained model can legitimately be
applied, which is directly the question "can a model trained on my 144 stations be applied to a
location that is not one of them?"

Do not, however, take spatial cross-validation as automatically correct.
[Wadoux et al. 2021](https://doi.org/10.1016/j.ecolmodel.2021.109692) argue the counter-case — that spatial CV is
*pessimistically* biased when the goal is map accuracy over a defined area with a probability sample,
and that the appropriate design depends on the inference you want. The synthesis is that your CV
design must mirror your intended use: if you intend to post-process at *these* stations for *future*
dates, you need temporal blocking and station-wise pooling; if you intend to predict at *new*
locations, you need spatial blocking and must expect lower and more honest scores. Decide which claim
you are making before you choose folds.

For empirical evidence that this changes conclusions rather than just decimal places, two papers do
the work. [Sweet et al. 2023](https://doi.org/10.1175/aies-d-23-0026.1) demonstrate directly on spatiotemporal
climate data that CV strategy alters both measured performance *and* model interpretation — the
feature importances change, not merely the skill — and find that feature-space clustering CV
generalised best to held-out years and regions. [Ploton et al. 2020](https://doi.org/10.1038/s41467-020-18321-y)
is the cautionary case study: a high-profile large-scale ecological mapping exercise whose reported
performance collapsed under spatially explicit validation. The broader taxonomy of how this goes wrong
across ML-based science, with a reproducibility checklist you can actually follow, is
[Kapoor and Narayanan 2023](https://doi.org/10.1016/j.patter.2023.100804).

For protocol conventions specific to your task, [Vannitsem et al. 2020](https://doi.org/10.1175/bams-d-19-0308.1)
is the best single orientation paper on statistical post-processing — methods, evaluation practice and
open challenges — and [Rasp and Lerch 2018](https://doi.org/10.1175/mwr-d-18-0187.1) is the reference
neural-network post-processing study for station temperature over a dense network, including the
station-embedding trick that lets one model serve many stations. On the downscaling side,
[Gutiérrez et al. 2018](https://doi.org/10.1002/joc.5462) is the **VALUE** perfect-predictor cross-validation
experiment: an intercomparison of a large ensemble of statistical downscaling methods over Europe with
a defined battery of marginal, temporal, spatial and extremal validation indices. Adopt VALUE's index
battery as a template — it is the closest thing the downscaling community has to an agreed evaluation
protocol. [Baño-Medina, Manzanas and Gutiérrez 2020](https://doi.org/10.5194/gmd-13-2109-2020) gives concrete
configuration and intercomparison of deep-learning downscaling models, and
[Rampal et al. 2024](https://doi.org/10.1029/2024gl112492) documents a generative downscaler failing to
extrapolate precipitation extremes to warmer climates — a reminder that a model validated in-sample
may have learned nothing transferable.

## Question 9: Baselines — what would count as an achievement?

A skill score is a claim about a comparison, and it is only as meaningful as its reference. The
hydrological forecasting community states the standard most bluntly:
[Pappenberger et al. 2015](https://doi.org/10.1016/j.jhydrol.2015.01.024) argue that a method which beats the raw
forecast but not climatology has achieved nothing, and lay out how to construct and report benchmarks
in ensemble prediction. [Harrigan et al. 2018](https://doi.org/10.5194/hess-22-2023-2018) applies a concrete
benchmark hierarchy — climatology, persistence, raw forecast — to an operational ensemble system, and
is a good template for what a benchmark table should look like.

Two papers explain why the reference must be constructed carefully rather than picked casually.
[Mason 2004](https://doi.org/10.1175/1520-0493(2004)132%3C1891:oucaar%3E2.0.co;2) shows that "climatology" as
a reference strategy in the Brier and ranked probability skill scores is ambiguous — there are several
defensible constructions and they give different verdicts. More seriously,
[Hamill and Juras 2006](https://doi.org/10.1256/qj.06.25) demonstrate that skill scores can be inflated *purely*
by variation in the underlying climatology across the samples being pooled. This is the paper with the
sharpest implication for your specific setup: you have 144 stations spanning 55–70.5°N, from the
Baltic coast to Arkhangelsk, with wildly different temperature climatologies, and you are working in a
region with a strong seasonal cycle. **Pool those stations and seasons against a single climatological
reference and you will manufacture skill that has nothing to do with your model.** The remedy is a
station-specific and seasonally-varying (e.g. day-of-year windowed) climatology, and skill reported
per station and per season before any aggregation. WeatherBench 2
([Rasp et al. 2024](https://doi.org/10.1029/2023ms004019)) is worth consulting here too for its baseline choices,
including a probabilistic climatology built by treating individual years as ensemble members.

## Question 10: Significance, multiplicity, and 144 stations

Once you have score differences you will want to say whether they are real, and the verification
samples are correlated in both time and space, so nominal confidence intervals will be too narrow.
[Jolliffe 2007](https://doi.org/10.1175/waf989.1) is the entry point for uncertainty and inference on verification
measures, including block and bootstrap approaches for correlated samples;
[Ferro 2007](https://doi.org/10.1175/waf1034.1) treats the specific case of comparing probabilistic systems with
the Brier score including sampling uncertainty; and
[Siegert et al. 2016](https://doi.org/10.1175/mwr-d-16-0037.1) provides statistical testing and power analysis for
detecting improvements in correlation skill — power analysis being the part usually skipped, and the
part that tells you whether your sample can detect a 2% effect at all. From the econometrics side,
[Diebold 2015](https://doi.org/10.1080/07350015.2014.983236) revisits the Diebold–Mariano test twenty years on,
including its use and abuse for autocorrelated loss differentials, which is exactly the structure of a
forecast-score comparison.

The multiplicity problem deserves separate emphasis because your design invites it. If you test 144
stations at the 5% level you expect roughly seven spurious "significant" stations even if your method
does nothing at all. [Wilks 2016](https://doi.org/10.1175/bams-d-15-00267.1) is the field's standard rebuke of
grid-point-wise significance testing — the paper that named the "stippling shows statistically
significant grid points" problem — and it prescribes a false-discovery-rate control procedure as the
fix. Apply FDR across your stations; do not report per-station significance uncorrected.

## Question 11: Extremes, and why you cannot simply score the cold days

You will be tempted to evaluate specifically on extreme events — the severe cold outbreaks that matter
in Murmansk and Arkhangelsk. There is a trap here with a name.
[Lerch et al. 2017](https://doi.org/10.1214/16-sts588) describe the **forecaster's dilemma**: if you select
verification cases by the *observed* outcome and then apply a proper score, you destroy propriety, and
the procedure systematically favours forecasters who exaggerate. Restricting your verification sample
to observed cold extremes is not a neutral zoom; it is a corrupted experiment. The correct approach is
a **weighted** proper score, which up-weights the region of interest while retaining propriety.
[Taillardat, Zamo and colleagues 2022](https://doi.org/10.1016/j.ijforecast.2022.07.003) develop CRPS-based
approaches for evaluating forecasts of extremes without losing propriety, and
[Biegert et al. 2026](https://arxiv.org/abs/2606.21170) (preprint) proposes a weighted *potential* CRPS specifically for
fair comparisons of AI and physics-based models on extreme events — combining the fairness theme of
Question 4 with the extremes theme here, and representing the current frontier of this argument.

---

## A concrete evaluation protocol you can adopt now

Synthesising the above into something you can implement before writing any modelling code. This is
the deliverable of this track.

1. **Declare the target functional and score set in advance.** Primary score: fair CRPS on the raw and
   post-processed ensembles, computed with a verified implementation
   ([Jordan et al. 2019](https://doi.org/10.18637/jss.v090.i12)) and never the naive estimator. Decompose it into
   reliability and potential CRPS ([Hersbach 2000](https://doi.org/10.1175/1520-0434(2000)015%3C0559:dotcrp%3E2.0.co;2))
   so you can say whether you fixed calibration or added information.
2. **Report a variance or spectral diagnostic alongside every averaging score.** A variance ratio
   (forecast variance / observed variance) per station and season, plus threshold-exceedance
   categorical scores. Without this, your evaluation rewards smoothing
   ([Bonavita 2024](https://doi.org/10.1029/2023gl107377); [Rasp et al. 2024](https://doi.org/10.1029/2023ms004019)).
3. **Build a three-tier baseline table before building any model:** raw AIFS ENS, station-specific
   day-of-year climatology (as a probabilistic climatology, not a single mean), and persistence. Report
   skill against all three ([Pappenberger et al. 2015](https://doi.org/10.1016/j.jhydrol.2015.01.024);
   [Harrigan et al. 2018](https://doi.org/10.5194/hess-22-2023-2018)). Never pool stations against a common
   climatology ([Hamill and Juras 2006](https://doi.org/10.1256/qj.06.25)).
4. **Split by time in contiguous blocks with buffers.** Whole years or seasons for test, with a gap of
   at least several days between train and test blocks ([Racine 2000](https://doi.org/10.1016/s0304-4076(00)00030-0)).
   Hold out final years entirely, untouched, for a single final evaluation.
5. **Additionally split by station if you claim spatial transferability.** Leave-station-out or
   spatially blocked folds, with hyperparameter tuning nested inside
   ([Roberts et al. 2016](https://doi.org/10.1111/ecog.02881); [Schratz et al. 2019](https://doi.org/10.1016/j.ecolmodel.2019.06.002)).
   Report both the in-station and out-of-station numbers; the gap between them is the honest measure
   of what you have learned.
6. **Never compare across ensemble sizes with an unfair score,** and correct the spread–skill target
   by √((M+1)/M) ([Ferro 2013](https://doi.org/10.1002/qj.2270); [Fortin et al. 2014](https://doi.org/10.1175/jhm-d-14-0008.1)).
7. **Add observation-error variance before judging dispersion**
   ([Sætra et al. 2004](https://doi.org/10.1175/1520-0493(2004)132%3C1487:eooeot%3E2.0.co;2)) — and remember
   that your station-versus-grid elevation mismatch of −128 to +72 m is a representativeness error on
   top of instrument error.
8. **Use CORP reliability diagrams and rank histograms per station or per homogeneous group, never
   pooled** ([Dimitriadis et al. 2021](https://doi.org/10.1073/pnas.2016191118);
   [Marzban et al. 2010](https://doi.org/10.1175/2010mwr3129.1)).
9. **Control the false discovery rate across stations**
   ([Wilks 2016](https://doi.org/10.1175/bams-d-15-00267.1)) and report block-bootstrap intervals on score
   differences ([Jolliffe 2007](https://doi.org/10.1175/waf989.1)).
10. **Evaluate extremes with weighted proper scores, not by subsetting on the observed outcome**
    ([Lerch et al. 2017](https://doi.org/10.1214/16-sts588)).

## What this means for a NW-Russia AIFS downscaling project

Three points from this track change what you should do, rather than merely how you should describe it.

**Your effect size and your bookkeeping errors are the same size.** The gains measured so far in this
project are around 2%, one method at +2.2% and two negative. The unfair-CRPS artefact at 51 members is
1.96%. The spread–skill correction at 51 members is about 1%. The interpolation-method choice
([Accadia et al. 2003](https://doi.org/10.1175/1520-0434(2003)018%3C0918:sopfss%3E2.0.co;2)) is of comparable
magnitude. This means the protocol is not hygiene you apply at the end — at your effect size, an
imperfect protocol will *determine* your conclusions. Fix the protocol first, then model.

**The station-only observation set is a strength for forecast verification, and the missing
precipitation is less costly here than it looks.** The literature's biggest verification headaches —
double penalty, neighbourhood scale selection, gridded-analysis contamination — are largely
precipitation-and-grid problems. You have temperature, dew point and wind at 99–100% completeness at
points, verified against a forecast that has not assimilated them. That is a *cleaner* verification
experiment than most of the AI-weather papers cited above manage, because
[Ben Bouallègue et al. 2024](https://doi.org/10.1175/bams-d-23-0162.1) had to argue for observation-based
verification against a field that defaults to analysis-based verification. Lean into it.

**There is a real, occupiable gap.** Station-level probabilistic verification of AI ensemble forecasts
over a sparse, high-latitude, orographically awkward network with large representativeness errors is
not covered by the existing protocol literature. The AI-verification papers verify on grids against
analyses; the post-processing protocol papers work over dense mid-latitude networks; the spatial
verification literature assumes gridded truth. A study that (a) applies fair scores correctly,
(b) reports a variance diagnostic alongside CRPS, (c) uses temporally *and* spatially blocked CV with
explicit in-station versus out-of-station reporting, and (d) treats elevation mismatch as
representativeness error rather than as model error, would be methodologically ahead of a good deal of
published work — regardless of whether the downscaling itself succeeds. That is worth knowing: this
track's protocol is not just a defensive measure, it is a potential contribution.

---

## Annotated reading order

Read in this order; the first four are non-negotiable.

1. [Gneiting, Balabdaoui and Raftery 2007](https://doi.org/10.1111/j.1467-9868.2007.00587.x) — *calibration and
   sharpness*. The organising principle. Read this before anything else; every later decision
   references it.
2. [Ferro 2013](https://doi.org/10.1002/qj.2270) — *fair scores*. Short, and it changes your code on the first
   day. Follow with [Ferro et al. 2008](https://doi.org/10.1002/met.45) for the CRPS-specific magnitude and
   [Leutbecher 2018](https://doi.org/10.1002/qj.3387) for how many members you need.
3. [Rasp et al. 2024](https://doi.org/10.1029/2023ms004019) — *WeatherBench 2*. The reference protocol for
   evaluating data-driven models, with the blurring-versus-SEEPS reversal that motivates your whole
   evaluation design. Pair with [Bonavita 2024](https://doi.org/10.1029/2023gl107377) for the spectral diagnosis.
4. [Roberts et al. 2016](https://doi.org/10.1111/ecog.02881) — *blocked cross-validation*. Not a meteorology
   paper, but the clearest statement of the splitting problem you face. Pair with
   [Sweet et al. 2023](https://doi.org/10.1175/aies-d-23-0026.1) for the demonstration on climate data.
5. [Vannitsem et al. 2020](https://doi.org/10.1175/bams-d-19-0308.1) — *statistical post-processing review*. The
   best single orientation to your actual task, once you understand the scores.
6. [Hersbach 2000](https://doi.org/10.1175/1520-0434(2000)015%3C0559:dotcrp%3E2.0.co;2) — *CRPS
   decomposition*. Short and immediately practical; this is the diagnostic you will run most often.
7. [Hamill and Juras 2006](https://doi.org/10.1256/qj.06.25) — *is it real skill?* Read before you aggregate
   anything across your 144 stations.
8. [Ben Bouallègue et al. 2024](https://doi.org/10.1175/bams-d-23-0162.1) — *operational assessment of AI
   forecasts*. The closest published analogue to the verification you are about to do.
9. [Gutiérrez et al. 2018](https://doi.org/10.1002/joc.5462) — *VALUE*. Steal the validation index battery.
10. [Roberts and Lean 2008](https://doi.org/10.1175/2007mwr2123.1) and [Ebert 2008](https://doi.org/10.1002/met.25) — *spatial
    verification*. Read for the mechanism (why grid scores prefer blur), not for direct application to
    a point network.
11. [Nurmi 1994](https://doi.org/10.21957/dx25q07hu) — *local forecast verification*. Old, unglamorous, and the
    most directly applicable checklist for station work in the whole list.
12. [Lang et al. 2024](https://arxiv.org/abs/2412.15832) (preprint) — *AIFS-CRPS*. Read last, once the scoring theory is
    in place, because it is about the training objective of the model you intend to use.
