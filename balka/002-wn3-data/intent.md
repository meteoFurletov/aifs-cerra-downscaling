# Intent: WN3 2 m temperature ensembles over the domain

Author: Nikita Furletov. Owner: Nikita Furletov. Status: accepted. Date: 2026-09-27.
Resumed 2026-10-02: WeatherNext access granted.

## Problem

Part of [001-weathernext3](../001-weathernext3/intent.md). We hold no WN3 data yet; access was
granted on 2026-10-02. We do not know how large the ensembles are over our domain, or how much
of the comparison B window (2025-07 → 2026-05) the archive covers.

## Outcome

WN3 2 m temperature, all members, is loadable next to AIFS ENS for the domain, the leads
we score and a period we chose knowing its size and coverage.

## Behaviours

- Access to WN3 data is granted and usable from a cloud session.
- Before any bulk download, we know the size per day and per lead of WN3 over the domain, and which dates the archive holds.
- The period is chosen from that and recorded with the reason.
- Every WN3 member is kept, not only the mean and spread.
- Samples line up with AIFS ENS by valid time and lead.
- WN3 loads the same way as the other sources, and the existing source checks still all pass.

## Out of scope

- Any scoring; that is the later children of 001.
- WN3 variables other than 2 m temperature.

## Open questions

- Access from a cloud session: the `wn3-reader` key must be in the environment, and it is unchecked whether the grant covers that service account as well as the account on the form.
- Whether WN3 becomes a sixth canonical source on the HF dataset or stays local; the size decides.
- Training leakage: WN3's production model was trained on data, station reports included, up to 2026-06-30, so it may have seen the whole comparison B window (2025-07 → 2026-05). Which model version produced each archived period decides the period: that window, if it came from versions trained only on earlier years; otherwise runs from 2026-07 on, after the cutoff.
