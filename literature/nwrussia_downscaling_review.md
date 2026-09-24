# Downscaling NWP over Northwest Russia: a regional literature review

**Domain of interest:** 55–70.5°N, 26–46°E — Pskov/Novgorod north to Murmansk, Baltic coast east to Arkhangelsk/Vologda.
**Question this review answers:** what has the field already established about statistical downscaling and forecast post-processing at these latitudes, what mesoscale physics must a downscaling model capture here, and what open data exists to train and verify against.

**Search effort behind this document:** 77 keyword queries against OpenAlex across seven vocabulary families, 24 citation-graph traversals (backward references + forward citations) seeded on the most on-target hits, 5 arXiv queries plus targeted preprint fetches, and 10 deliberate negative-confirmation queries. 1623 unique records retrieved; 61 carried through to the citation table. No retracted works among them.

---

## 1. Headline findings

1. **Nobody has done this.** Statistical downscaling or ensemble post-processing of NWP, verified against stations, inside this specific box, does not appear in the indexed literature. This is an evidenced negative (Section 7), not an artefact of weak searching. The project would be occupying genuinely open ground rather than reproducing existing work.
2. **The 1.31 K ERA5 floor already measured in this project is not a failure of method — it is close to the theoretical floor, and the literature says so.** Køltzow et al. (2022) estimate that 50–60% of the total near-surface temperature MAE between reanalyses and station observations is *representativeness error* — sub-grid variability the gridded field could not possibly reproduce (doi:10.33265/polar.v41.8002). Göber & Zsótér (2008) demonstrate the same point structurally: a *perfect* model verified against point observations still scores badly, with the error from wrong-kind verification being of the same order as the forecast error itself (doi:10.1002/met.78). This reframes the earlier negative result as expected physics, and it sets the correct baseline for any future comparison.
3. **CERRA is the strategically important find.** A 5.5 km regional reanalysis of Europe, 1984–2021, freely licensed through Copernicus, with a 10-member 11 km ensemble and a separate land-surface analysis (doi:10.1002/qj.4764). If its domain covers this box — see the verification note in Section 4 — it is a plausible answer to the precipitation truth-data problem that the station archive cannot solve.
4. **The dominant mesoscale phenomenon in this domain has been simulated, and the numbers are specific.** Gulf of Finland snow bands: quasi-stationary precipitation lines exceeding 300 km in length, driven by ~18 K land–sea potential temperature contrast, easterly winds of 12–14 m/s, fetch of 200–300 km, and colliding land breezes producing a sea-level convergence of Δv ≈ 16 m/s across ~7 km with ~0.9 m/s vertical motion (doi:10.3402/tellusa.v67.25102). A 0.25° forecast field resolves none of this.
5. **The winter urban heat island inside this box is large and has been quantified — at Apatity, not St Petersburg.** Up to 11 K instantaneous, 1.9 K winter mean, with at least 50% attributed to the UHI effect and that in turn driven mostly by *direct anthropogenic heating* (doi:10.5194/acp-18-17573-2018). Apatity (67.567°N, 33.393°E) sits inside the domain. St Petersburg — the largest city in the box — is essentially undocumented.
6. **Fine-tuning an existing AI forecast model for regional downscaling is an established, published pattern, not an improvisation.** Koldunov et al. propose using existing AI-NWP systems directly as downscaling tools (arXiv:2406.17977); Munir et al. demonstrate efficient localized adaptation of a neural forecast to one region (arXiv:2409.07585). Both are compute-feasible framings for a 4 GB GPU in a way that training from scratch is not.

---

## 2. The verification problem comes first

This section is placed first deliberately: it determines what "success" can even mean for this project.

**Point observations do not measure what a gridded model predicts.** Göber & Zsótér constructed a "perfect model" by averaging high-density observations to the grid box, then verified it against the point observations it was built from. It scored poorly, and worse as events became more severe; their conclusion is that the baseline for comparison is not the theoretical best score but the score a perfect model achieves (doi:10.1002/met.78). Any claim that a post-processing method "failed to beat ERA5" needs this baseline computed before it means anything.

**At high latitudes the representativeness component is measurable and large.** Køltzow et al. approximated it empirically from station pairs — 15 pairs 0.5–3.0 km apart to stand for a 2.5 km grid, 44 pairs 10–30 km apart to stand for ERA5's ~31 km grid — and found the T2m representativeness error slightly above 0.5 °C in winter for the fine grid and slightly above 1.0 °C in winter for the ERA5-scale grid. The median representativeness error is 50–60% of total MAE for most months in *both* reanalyses; for 10 m wind speed it reaches 40–55% in CARRA and 60–70% in ERA5 (doi:10.33265/polar.v41.8002). They also note this is a *moderate* approximation, since a model's effective resolution is coarser than its grid spacing.

**Height difference is an identified and partly correctable component of it.** The same study applies a simple 0.65 °C/100 m height correction before computing MAE, and reports 10–15% error reduction in summer in both reanalyses (doi:10.33265/polar.v41.8002). Sheridan & Smith's height-based downscaling correction for complex terrain is the general method (doi:10.1002/met.177). Given that station elevation minus ERA5 orography spans −128 to +72 m in this domain, this is the correct minimal baseline for any station correction to beat — and the earlier finding that a naive lapse rate gave −1.3% is itself informative, suggesting the residual is not dominated by height at these stations.

**Practical consequence.** Compute the perfect-model / representativeness floor for the 144-station network *before* the next round of method comparison. Station pairs within the network at 0.5–3 km and 10–30 km separations give the same empirical estimate Køltzow et al. used. Without it, a method that recovers 2% is indistinguishable from a method that recovers most of the available signal.

---

## 3. High-latitude and boreal downscaling: what has been done and what worked

**The wintertime stable boundary layer is the identified error regime.** Atlaskin & Vihma evaluated NWP wintertime nocturnal boundary-layer temperatures over Europe and Finland (doi:10.1002/qj.1885) — the canonical statement of this problem at these latitudes, and the reason winter is where a post-processor has the most to gain. Sandu et al. explain *why* stably stratified conditions are systematically hard for NWP (doi:10.1002/jame.20013), and Holtslag et al. give the community review of stable boundary layers and diurnal cycles as a model challenge (doi:10.1175/bams-d-11-00187.1). Zhang et al. supply the radiosonde climatology of Arctic surface-based inversions — frequency, depth, strength (doi:10.1175/2011jcli4004.1). Together these say: the error a downscaling model must learn here is not random noise, it is a structured, physically-understood, strongly seasonal bias associated with surface-based inversions and cold pooling.

**Method-comparison design is settled at the European scale.** The VALUE intercomparison evaluated a large ensemble of statistical downscaling methods over Europe under perfect-predictor conditions (doi:10.1002/joc.5462) — the reference experimental design for comparing methods fairly, and worth copying rather than reinventing. Murphy's earlier statistical-versus-dynamical downscaling comparison (doi:10.1175/1520-0442(1999)012<2256:aeosad>2.0.co;2) is the founding statement of why statistical approaches remain competitive with dynamical ones.

**Convection-permitting dynamical downscaling over Fennoscandia has demonstrable added value, but it is not reachable on local compute.** Lind et al. produced the first long-term 3 km HCLIM simulation over Fenno-Scandinavia and document where km-scale resolution matters (doi:10.1007/s00382-020-05359-3). Haakenstad et al.'s NORA3 is a 3 km ERA5-driven hindcast over the Nordic region with published precipitation and temperature statistics in complex terrain (doi:10.1175/jamc-d-22-0005.1). Read these for *what* km-scale resolution buys — that is the target a statistical method is trying to emulate cheaply — not as a workflow to reproduce.

**Regional Arctic NWP configuration and observation impact.** Müller et al. describe AROME-Arctic, a convection-permitting operational system for the European Arctic (doi:10.1175/mwr-d-17-0194.1); Køltzow et al. examine how to configure a regional Arctic NWP system to maximise predictive capability (doi:10.1080/16000870.2021.1976093); Randriamampianina et al. quantify the relative impact of Arctic conventional versus satellite observations on regional forecast skill (doi:10.1002/qj.4018). Relevant here mainly as evidence of how much of regional skill comes from observations rather than resolution — which matters for a region where the observation network is sparse and access-restricted.

**No study in this group verifies inside the target box.** CARRA-East covers Svalbard, the Barents Sea, and northern Norway, Sweden and Finland (doi:10.33265/polar.v41.8002) — it reaches the Kola Peninsula but not Pskov, Novgorod, Vologda or Arkhangelsk. The Nordic products stop at national borders. This is the geographic gap.

---

## 4. Regional reanalysis: the possible answer to the precipitation problem

**CERRA.** Ridal et al. describe a regional reanalysis over a domain covering Europe, 1984–2021, produced under the Copernicus Climate Change Service: a 5.5 km deterministic run, a 10-member 11 km ensemble data assimilation (CERRA-EDA), and an offline surface analysis (CERRA-Land). It is built from HARMONIE cy40 with back-phased physics from cy42, and assimilates conventional observations, satellite radiances, atmospheric motion vectors, radio-occultation bending angles, GNSS zenith total delay, and *local surface observations rescued from historical archives at national meteorological services*. The reanalyses show added value over global ERA5 for almost all surface variables, most clearly in smaller areas with complex terrain (doi:10.1002/qj.4764). Wang & Randriamampianina detail the satellite radiance assimilation component (doi:10.3390/rs13030426).

> **Verify before committing.** The published system description states a pan-European domain but does not pin the eastern boundary. Whether the CERRA grid reaches 46°E across the full 55–70.5°N span — and how many of the 144 stations fall inside it with an interior (not boundary-relaxation) grid point — is the single highest-value data check to run next. It is a cheap check and it decides whether this project has 5.5 km precipitation truth data or does not.

Note also the assimilation-circularity caveat that already bit this project with ERA5 and SYNOP: CERRA assimilates local surface observations. If those include the same stations, CERRA's surface analysis is partly pinned to them too, and the same "no method beats the analysis" result should be expected. This does *not* undermine using CERRA as a **forecast** downscaling target or as a precipitation field — CERRA precipitation is not assimilated the way temperature is — but it does mean a temperature-verification experiment against CERRA analysis needs the same scepticism.

**Comparative benchmarking of gridded products has been done and is worth copying.** Monteiro & Morin compare ERA5, ERA5-Land, CERRA-Land and UERRA MESCAN-SURFEX for winter temperature, precipitation and snow (doi:10.5194/tc-17-3617-2023) — a directly reusable evaluation template. Cavalleri et al. inter-compare and validate high-resolution surface air temperature reanalysis fields including CERRA against dense station data (doi:10.1002/joc.8475). Kaiser-Weiss et al. synthesise the UERRA project's finding on added value of regional reanalyses and the spread between three independent systems (doi:10.1088/2515-7620/ab2ec3). Kaspar et al. review the DWD COSMO regional reanalyses down to 2 km and their access conditions (doi:10.5194/asr-17-115-2020).

**Other open gridded resources for this box.**

- **ERA5-Land** — 9 km land reanalysis, openly licensed, covers the domain (doi:10.5194/essd-13-4349-2021). A plausible intermediate predictor field between ERA5 and station scale.
- **E-OBS** (ensemble version) — European gridded daily temperature and precipitation from stations with explicit uncertainty estimates (doi:10.1029/2017jd028200). Its station density collapses east of the EU border, so the uncertainty field itself is the useful part here: it maps where the product should not be trusted, which is most of this box.
- **HadISD** — quality-controlled sub-daily station data derived from ISD (doi:10.5194/gi-5-473-2016). This is the QC pipeline for the exact archive already in use, and the right place to check whether the 0% precipitation population is an archive-construction artefact or genuinely absent upstream.
- **seNorge_2018** — 1 km daily gridded precipitation and temperature over Norway from station interpolation (doi:10.5194/essd-2019-43). Included as a demonstration of what a well-resourced national gridded product looks like, and hence what does *not* exist openly for this domain.
- **Snow fields are a known weak point.** Kouki et al. evaluate snow cover properties in ERA5 and ERA5-Land against satellite datasets (doi:10.5194/tc-17-5007-2023) — relevant because snow-albedo state drives much of the winter surface temperature error a downscaling model would be correcting.
- **NETCID** — gridded North Eurasian thermal comfort indices (doi:10.1088/1748-9326/ac7fa9). Notable less for the product than for its stated rationale: it is built from reanalysis precisely *because* in-situ observations over Northern Eurasia are sparse. That is an independent, published statement of this project's core constraint.
- **PEEX** — the Pan-Eurasian Experiment research framework for northern Eurasia (doi:10.5194/acp-16-14421-2016). The most plausible open route to regional collaborators and data for someone without institutional access.

**On Roshydromet / RIHMI-WDC:** searches for an openly-accessible Roshydromet or RIHMI-WDC station archive returned nothing describing one (Section 7). The literature that uses Russian station data does not describe an open access route to it. Plan on NOAA ISD-Lite plus reanalysis, and treat any Russian national archive as unavailable unless proven otherwise.

---

## 5. The regional physics a 0.25° model will miss

### 5.1 Sea- and lake-effect convection — the signature phenomenon of this domain

**Gulf of Finland snow bands are simulated, mechanistically explained, and quantified.** Mazon et al. used WRF with radar verification for January 2006 and February 2012. Findings: a quasi-stationary precipitation line greater than 300 km long elongated east–west over the gulf; easterly surface winds of 12–14 m/s with fetch 200–300 km; a land–inland versus sea air potential temperature difference around 18 K driving strong land breezes from both the Finnish and Estonian coasts, converging offshore with vertical motion around 86 cm/s; two easterly low-level jets, one over each coast, with core speeds ~13 and ~14 m/s at 500–800 m; and at sea level a convergence of Δv ≈ 16 m/s across roughly 7 km, forcing ~0.9 m/s vertical motion between 500 and 900 m (doi:10.3402/tellusa.v67.25102). They also reproduce the established thresholds: bands form above 10 m/s wind speed, and for a wind-speed-to-fetch ratio V/L between 0.02 and 0.09 m/s/km.

**The idealised mechanism paper is explicitly configured for this gulf.** Savijärvi simulated a 2-D cold-air outbreak across an 80 km non-frozen gulf at 60°N (doi:10.3402/tellusa.v64i0.12244), with a follow-up on the effect of wind speed on snow bands along a non-frozen sea channel (doi:10.1007/s00703-015-0370-8). Read these for the mechanism in its cleanest form.

**Baltic and Finnish-coast analogues extend the picture.** Jeworrek et al. modelled convective snow bands along the Swedish east coast with a coupled atmosphere–ocean–wave system (doi:10.5194/esd-8-163-2017). Olsson et al. derived the statistics of sea-effect snowfall along the Finnish coastline from regional climate model data, defining the favourable conditions (doi:10.5194/asr-17-87-2020), and documented an intense case in western Finland — 73 cm of snow (31 mm liquid equivalent) in under a day, with a very small spatial footprint (doi:10.5194/asr-14-231-2017). That footprint is the argument for downscaling in one sentence. Rutgersson et al. review natural hazards and extreme events across the Baltic Sea region (doi:10.5194/esd-13-251-2022), and there is a general review of forecasting lake- and sea-effect snowstorms with its advancements and challenges (doi:10.1002/wat2.1594) as an entry point to the subfield.

### 5.2 Ladoga and Onega: a genuine hole, but a well-signposted one

**No mesoscale meteorological modelling study of Lake Ladoga or Lake Onega surfaced.** Targeted queries returned lake limnology, water-level altimetry and ecology (Section 7). For Europe's two largest lakes, sitting in the middle of the target domain, this is a striking absence — and one of the clearest research openings identified in this review.

**But the general machinery for lake effects in NWP exists and is documented.** Balsamo et al. showed that adding the FLake model to the ECMWF IFS changes near-surface temperature forecasts, establishing lake representation as a first-order forecast issue rather than a refinement (doi:10.3402/tellusa.v64i0.15829). Samuelsson et al. quantified the lake-induced 2 m temperature signal across Europe by comparing regional climate simulations with and without lakes (doi:10.60910/3pj6-v2hf). Rontu & Eerola validated HIRLAM's prognostic lake surface state — FLake plus an objective lake surface water temperature analysis — against in-situ measurements (doi:10.5194/gmd-12-3707-2019), and Eerola & Rontu showed that different lake surface temperature and ice-cover treatments produce different screen-level temperatures, with effects that remain local to areas near lakes (doi:10.60910/mc88-ndnz). Choulga & Kourzeneva's mean-depth estimation for boreal lakes (the GLDB database) is the ancillary data that determines how well any model treats Ladoga and Onega (doi:10.3402/tellusa.v66.21295). Batrak et al.'s thermodynamic sea-ice scheme work reports 2 m temperature MAE reaching 1.5 °C at +15 h for Svalbard when ice properties are misrepresented (doi:10.5194/gmd-11-3347-2018) — a calibration of how much frozen-surface state matters.

**Open observational route to lake state.** A 35-year AVHRR lake surface water temperature record exists for European lakes (doi:10.3390/rs10070990), and Kostianoy & Lebedev document interannual water-level variability of Ladoga and Onega from satellite altimetry (doi:10.3390/rs14030659). Both are openly-licensed remote sensing — a way to get lake surface state as a predictor without institutional data.

**Implication for feature engineering.** Distance-to-water, lake/sea surface temperature, ice cover, and land–water potential temperature contrast are not speculative predictors here. They are the exact quantities the mechanism papers identify as controlling. Ice-cover state in particular switches the phenomenon on and off.

### 5.3 Winter inversions and cold pooling

Covered mechanistically in Section 3 (doi:10.1002/qj.1885, doi:10.1002/jame.20013, doi:10.1175/bams-d-11-00187.1) and climatologically by the Arctic radiosonde inversion climatology (doi:10.1175/2011jcli4004.1). The operational point: winter cold-pool and inversion errors are where a station-level post-processor has the largest and most systematic signal to exploit, and they are strongly conditional on wind speed, cloud cover and snow state — which suggests those as interaction predictors rather than additive ones.

### 5.4 Urban heat island — documented by proxy, not at St Petersburg

**The one quantified UHI study inside the box is at Apatity.** Varentsov et al. combined a dense in-situ network, satellite land surface temperature, and 1 km model experiments run with and without urban surface parameterisation. Apatity (67.567°N, 33.393°E, Murmansk Oblast, ~60,000 inhabitants, January mean −13.5 °C, polar night) shows a persistent warm anomaly reaching up to 11 K in winter, with a wintertime mean 1.9 K higher in the city centre than the surrounding landscape. At least 50% is attributed to the UHI effect — driven mostly by *direct anthropogenic heating* — with the remainder from natural microclimatic variability over undulating relief. They note the UHI can be as large as the projected 21st-century regional warming (doi:10.5194/acp-18-17573-2018).

**St Petersburg itself is essentially undocumented.** A dedicated query returned a small total dominated by air-quality and Moscow studies (Section 7). By contrast the Moscow and Siberian-city UHI literature is well developed: Miles & Esau's remote-sensing survey of northern West Siberian cities was the first systematic UHI study north of 60°N (doi:10.3390/rs9100989); Varentsov et al. quantified local and mesoscale drivers of the Moscow UHI using reference *and* crowdsourced stations (doi:10.3389/fenvs.2021.716968) and separately evaluated Netatmo citizen weather stations for urban climate research in Moscow with an explicit uncertainty assessment (doi:10.1088/1755-1315/611/1/012055); the same group examined urban canopy parameters in COSMO/TERRA_URB for Moscow (doi:10.3390/atmos11121349) and the vertical structure of the urban boundary layer in a cold-climate Siberian city (doi:10.1016/j.uclim.2022.101351). Brozovsky et al. review urban climate research in cold and polar climates, which maps where the field's attention has gone (doi:10.1016/j.rser.2020.110551).

**Two practical consequences.** First, the Apatity numbers give a defensible prior for the magnitude of an urban predictor at high latitude — and the anthropogenic-heating attribution means the effect will not be captured by land-cover or impervious-fraction features alone. Second, the crowdsourced-station methodology is the realistic route to St Petersburg urban observations for someone without institutional access, and it has been validated in a Russian megacity by the same group.

---

## 6. AI forecast models as the base for downscaling

**The base model.** AIFS is a graph neural network encoder/decoder with a sliding-window transformer processor, trained on ERA5 and ECMWF operational NWP analyses (arXiv:2406.01465). AIFS-CRPS is the ensemble variant, trained with a loss based directly on the Continuous Ranked Probability Score (arXiv:2412.15832) — relevant because the accessible archive is the 51-member AIFS ENS. A later update to AIFS Single adds physical-consistency bounding layers and an expanded variable set, and reports that the physical constraints *substantially improve precipitation forecasts* (arXiv:2509.18994). Given that precipitation cannot be verified locally against the station archive, knowing which AIFS version's precipitation is trustworthy matters.

**The published pattern for what this project wants to do.** Koldunov et al. propose using existing AI-NWP systems as downscaling tools directly, on the argument that high-resolution models are computationally prohibitive and conventional downscaling is limited to small regions (arXiv:2406.17977). This is the closest published statement of the user's own instinct, and it should be read first among the preprints. Munir et al. demonstrate efficient localized adaptation of a neural weather forecasting model to a single region (arXiv:2409.07585) — the compute-feasible fine-tuning pattern. Wijnands et al. compare stretched-grid against limited-area approaches for data-driven regional forecasting with GNNs, including the boundary-condition trade-offs (arXiv:2507.18378) — read this before choosing an architecture, since the two options have very different data requirements.

**Verification standards for AI forecasts are now established, and should be adopted rather than improvised.** Ben Bouallègue et al. give the first systematic statistical assessment of ML-based weather forecasts at ECMWF (doi:10.1175/bams-d-23-0162.1). Olivetti & Messori ask directly whether data-driven models outperform numerical models for weather extremes in a semi-operational comparison including IFS HRES (doi:10.5194/gmd-17-7915-2024) — directly relevant to whether AIFS or IFS is the better base. Pasche et al. validate deep-learning forecast models on recent high-impact extreme events (doi:10.1175/aies-d-24-0033.1). Radford et al. compare AI weather prediction against NWP for 1–7 day precipitation (doi:10.1175/waf-d-24-0081.1) — read for method, since the truth data problem makes local replication of the precipitation part impossible.

---

## 7. The gap, with evidence

Ten deliberate negative-confirmation queries were run against the most specific regional framings. Result totals and top hits below. Small totals matter, but so do large totals whose top-ranked hits are off-topic — that pattern means the vocabulary exists in other fields and the intended topic does not exist at all.

| Query | Records matched | What the top hits actually were |
|---|---|---|
| Lake Ladoga lake-effect snow forecast | 154 | Global lake responses to climate change; RCM lake impacts; 1-D lake model performance — limnology and climate, no lake-effect snow |
| Lake Onega mesoscale meteorology model | 34 | Lake volume from space; RCM lake impacts; AVHRR lake surface temperature — remote sensing, no mesoscale meteorology |
| Statistical downscaling northwest Russia stations | 1110 | Global meteorological forcing dataset; US Pacific Northwest climate model; GCM-to-ecosystem downscaling — "northwest" matched the wrong continent |
| Post-processing ensemble forecast Russia stations temperature | 2350 | ERA-40 reanalysis; ensemble flood forecasting; FLUXNET2015 — generic term collision, nothing regional |
| Saint Petersburg urban heat island quantification winter | 146 | Urban biodiversity; St Petersburg emission monitoring campaign; global urban heat exposure — air quality, not UHI quantification |
| Leningrad oblast / Novgorod / Pskov meteorology forecast | 9 | Forest and peatland carbon storage; plant fungal contamination; forest sector economics — no meteorology whatsoever |
| Roshydromet station data archive open access | 135 | IGRA radiosonde archive; US Climate Reference Network; Norilsk oil spill monitoring — no description of an open Roshydromet archive |
| Downscaling AIFS regional high resolution station | 47 | ERA5 precipitation downscaling to km scale; regional AI typhoon model; decision-tree precipitation prediction — the method exists, this region does not |
| Karelia numerical weather prediction verification | 77 | HIRLAM lake temperature/ice effects; radiatively driven convection in ice-covered lakes; wildfire satellite assimilation — adjacent, not the target |
| AIFS ensemble post-processing station temperature Europe | 87 | AIFS-CRPS (twice, two versions); probabilistic solar forecasting model chains — the base model, no station post-processing over Europe |

**What this establishes.** The methods exist. The region's physics is partly documented. The intersection — a downscaling or post-processing study of NWP forecasts verified against stations in Northwest Russia — is unoccupied. Four specific, defensible research openings follow:

1. **Post-processing AIFS ENS to stations at 55–70.5°N, 26–46°E.** No published work does this anywhere in this box, with any model. Establishing the perfect-model floor first (Section 2) is what would make the result publishable rather than ambiguous.
2. **Lake-effect and sea-effect predictability over Ladoga, Onega and the Gulf of Finland in a global AI forecast.** The mechanism is quantified (doi:10.3402/tellusa.v67.25102) and the lakes are unstudied meteorologically. Asking whether AIFS at 0.25° represents any of the land–water contrast signal, and whether a statistical correction can recover it, is a well-posed and genuinely novel question.
3. **The winter inversion / cold-pool regime as a conditional post-processing problem.** The error is known to be structured and seasonal (doi:10.1002/qj.1885, doi:10.1175/2011jcli4004.1); no study has attempted to exploit that structure at station level in this domain.
4. **A St Petersburg urban temperature study using crowdsourced observations.** The methodology is validated in Moscow by the same research group (doi:10.1088/1755-1315/611/1/012055, doi:10.3389/fenvs.2021.716968), the high-latitude magnitude prior exists from Apatity (doi:10.5194/acp-18-17573-2018), and the city itself is undocumented. This is the lowest-barrier novel contribution in the list — it needs no HPC and no institutional data.

---

## 8. Reading order

**Tier 1 — read these five first (they change what you do next).**

1. Køltzow et al. 2022, *Polar Research* — doi:10.33265/polar.v41.8002. Why your ERA5 result was not a failure, and how to compute the floor you should have been comparing against. Read the representativeness-error section closely.
2. Göber & Zsótér 2008, *Meteorological Applications* — doi:10.1002/met.78. Short, and it reframes verification permanently. Read second so that the Køltzow numbers land properly.
3. Ridal et al. 2024, *QJRMS* — doi:10.1002/qj.4764. The CERRA system. Decide from this whether your truth-data problem is solvable, then verify the domain extent yourself.
4. Koldunov et al. 2024, arXiv:2406.17977. Your own idea, in the literature, with the argument for why it is the right approach given compute constraints.
5. Mazon et al. 2015, *Tellus A* — doi:10.3402/tellusa.v67.25102. The physics of your domain, quantified. This is the paper that tells you what features to build.

**Tier 2 — method and physics foundations.**

6. Atlaskin & Vihma 2012 — doi:10.1002/qj.1885. The winter error regime you will be correcting.
7. Sheridan & Smith 2010 — doi:10.1002/met.177. The baseline your method must beat.
8. Gutiérrez et al. (VALUE) 2018 — doi:10.1002/joc.5462. How to run a fair method comparison.
9. Varentsov et al. 2018 — doi:10.5194/acp-18-17573-2018. Magnitude of the high-latitude urban signal, inside your box.
10. Balsamo et al. 2012 — doi:10.3402/tellusa.v64i0.15829. Why lakes are a first-order forecast issue.
11. Ben Bouallègue et al. 2024 — doi:10.1175/bams-d-23-0162.1. How AI forecasts are properly verified.

**Tier 3 — consult when you reach that stage.**

12. Munir et al., arXiv:2409.07585 and Wijnands et al., arXiv:2507.18378 — when choosing a fine-tuning or regional architecture.
13. Moldovan et al., arXiv:2509.18994 and Lang et al., arXiv:2412.15832 — when selecting an AIFS version and reading its precipitation claims.
14. Monteiro & Morin 2023 — doi:10.5194/tc-17-3617-2023 — when benchmarking gridded products against each other.
15. Rontu & Eerola 2019 — doi:10.5194/gmd-12-3707-2019 and Choulga & Kourzeneva 2014 — doi:10.3402/tellusa.v66.21295 — when building lake-state predictors for Ladoga and Onega. Also Eerola et al. — doi:10.60910/mc88-ndnz and Samuelsson et al. — doi:10.60910/3pj6-v2hf, but note the metadata caveat below.
16. Olsson et al. 2020 — doi:10.5194/asr-17-87-2020 and Jeworrek et al. 2017 — doi:10.5194/esd-8-163-2017 — when working on the sea-effect snow case.
17. Varentsov et al. 2020 — doi:10.1088/1755-1315/611/1/012055 — when pursuing St Petersburg urban observations.
18. Dunn et al. 2016 (HadISD) — doi:10.5194/gi-5-473-2016 — when checking whether the precipitation gap in ISD-Lite is real or an artefact.

---

## 9. Coverage caveats

- **Russian-language literature is under-represented.** OpenAlex indexing of Roshydromet institutional journals — *Meteorologiya i Gidrologiya* and similar — is patchy, and searches in English-language vocabulary will miss work published only in Russian. COSMO-Ru specifically: queries surfaced no system-description paper meeting the citation bar for inclusion here. The negative in Section 7 should be read as "not present in the indexed international literature," which is weaker than "does not exist." A native-language search of Russian journal archives would be the natural complement to this review, and is the one gap in this survey that a reader could close themselves.
- **CERRA's eastern boundary is unverified.** Flagged in Section 4 because it is load-bearing for the whole truth-data strategy and cannot be settled from the published abstract.
- **Abstracts were unavailable in OpenAlex for 14 of the 44 shortlisted DOIs**, mostly older or paywalled journal articles. For the four papers whose specific numbers this review depends on, full texts were fetched and the quoted values read directly from the PDFs; for the others, relevance notes are based on title, venue and citation context rather than abstract text, and are correspondingly less specific.
- **Two DOIs have unreliable metadata in OpenAlex.** The two lake papers under DOI prefix 10.60910 (doi:10.60910/mc88-ndnz, doi:10.60910/3pj6-v2hf) are returned with a publication year of 2024 and a venue that is a Finnish labour-studies yearbook — both plainly inconsistent with their content, which is HIRLAM lake-surface and RCA/FLake regional climate work. The titles, authors and citation counts are consistent with real works and the science is cited here on that basis, but year and venue have been blanked in the citation table and should be taken from the publisher record before citing formally.
- **Some vocabularies failed.** arXiv queries containing the word "weather" without further qualification returned large numbers of space-weather papers; a Nordic-specific machine-learning query returned almost nothing on point. These were discarded rather than mined, so the arXiv coverage rests on the AIFS, post-processing, and limited-area framings.
- **No study verifying inside the target box was found in any vocabulary tried.** That is the review's central finding, and Section 7 is the evidence for it rather than an admission of incomplete searching.
