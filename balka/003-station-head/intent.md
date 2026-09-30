# Intent: a station head for 2 m temperature and dew point, after WN3

Author: Nikita Furletov. Owner: Nikita Furletov. Status: draft. Date: 2026-09-30.

## Problem

Our downscaling learns CERRA, so its station error can never beat CERRA's own (the floor in
[COMPARISONS.md §2](../../docs/COMPARISONS.md)). WN3 (Rasp et al. 2026) skips the reanalysis:
a station head, fitted to raw station reports, predicts 2 m temperature and dew point at any
point from the forecast and local geography, and beats global models at stations it never
saw. We do not know whether that method works on AIFS ENS with only the domain's SYNOP
stations, nor what it gives for dew point, which the project holds no data for yet.

## Outcome

We know whether a station head on AIFS ENS, fitted to the domain's SYNOP stations, beats raw
AIFS ENS at stations held out by location, for 2 m temperature and dew point, as an
ensemble, per lead and season.

## Behaviours

- Dew point observations sit alongside the temperature observations at the 299 stations, same period and quality control.
- AIFS ENS is held as 51 members for 2 m temperature and dew point.
- The station head predicts 2 m temperature and dew point as an ensemble at any point in the domain, from the AIFS ENS forecast and local geography.
- It learns only from stations in the training spatial folds and is scored at the held-out ones.
- Scores are CRPS, RMSE, bias and spread against error, per lead and season, against raw AIFS ENS; for temperature also against the CERRA nearest cell.
- Queried over the target window, it gives maps, checked for the artefacts WN3 reports: jumps between time steps and members biased warm or cold everywhere.

## Children (proposed)

1. `synop-dewpoint` — dew point at the 299 stations from the raw SYNOP bulletins.
2. `aifs-members` — AIFS ENS as 51 members, 2 m temperature and dew point; 001 reuses it if it resumes.
3. `station-head` — the head, trained and scored at held-out stations.
4. `station-head-grid` — the head queried over the target window: maps and artefact checks.

## Out of scope

- The 31 October write-up. This is exploratory, with no date.
- Wind, precipitation and other parameters; WN3 did not fit them to stations either.
- Stations outside the domain.

## Open questions

- Training length: AIFS ENS covers 11 months. Pre-training on ERA5 against the 2015–24 ISD archive, then fine-tuning on AIFS ENS (as stage 1 / stage 2 do), is one answer; design decides.
- Whether pseudo-stations drawn from CERRA or ERA5 anchor the head between stations, as WN3 does.
