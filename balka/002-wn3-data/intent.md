# Intent: WN3 2 m temperature ensembles over the domain

Author: Nikita Furletov. Owner: Nikita Furletov. Status: parked. Date: 2026-09-27.
Parked 2026-10-02: after the 31 October write-up, as its part two; every read before the Free Trial ends.

## Problem

Part of [001-weathernext3](../001-weathernext3/intent.md). We hold no WN3 data yet. The access
granted on 2026-10-02 covers `wn3-reader`, and `claude-cloud-meteof-weather` now pays for reading
all members. The archive holds runs from 2026-01-01 on, so of the comparison B window
(2025-07 → 2026-05) only 2026-01 → 2026-05 is there, and WN3 has no lead 0. WN3 is stored as
whole-globe fields ([estate](../../docs/estate.md), WN3 layout): daily runs over those five months
at our other five leads are ~6 TB raw or ~23 TB station-calibrated, however small our domain.

## Outcome

WN3 2 m temperature, raw and station-calibrated, all members, is loadable next to AIFS ENS
for the domain, the leads we score and a period we chose knowing its size and coverage.

## Behaviours

- WN3 is read with the `wn3-reader` key from Infisical.
- Before any bulk read, one run is processed first, and its measured size and cost are checked against the credit.
- The period is chosen from that and recorded with the reason.
- Every WN3 member is kept, not only the mean and spread, for both 2 m temperatures: raw at 0.1° and station-calibrated at 0.05°.
- Reading WN3 costs nothing beyond the $300 Free Trial credit: no upgrade to a paid account, and every read is done before the trial ends (90 days from 2026-10-02).
- Samples line up with AIFS ENS by valid time and lead. At lead 0, the +1 h of the run an hour earlier stands in, marked as a stand-in.
- WN3 loads the same way as the other sources, and the existing source checks still all pass.

## Out of scope

- Any scoring; that is the later children of 001.
- WN3 variables other than 2 m temperature.

## Open questions

- Whether WN3 becomes a sixth canonical source on the HF dataset or stays local; the size decides.
- Training leakage: WN3's production model was trained on data, station reports included, up to 2026-06-30, and all the archive holds of the comparison B window falls before that. Every run sits under `weathernext_3_0_0`, and the one run's metadata read names no model version, so nothing yet says those runs came from a model trained only on earlier years. Runs from 2026-07 on are clean but overlap none of our sources, which end 2026-05-31; using them means extending AIFS ENS, CERRA and SYNOP.
