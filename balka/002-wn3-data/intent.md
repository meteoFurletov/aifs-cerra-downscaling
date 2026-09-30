# Intent: WN3 2 m temperature ensembles over the domain

Author: Nikita Furletov. Owner: Nikita Furletov. Status: parked. Date: 2026-09-27.
Parked 2026-09-30: no access to WeatherNext data yet (request filed 2026-09-27, not granted).

## Problem

Part of [001-weathernext3](../001-weathernext3/intent.md). We hold no WN3 data and have no
access to it yet. We do not know how large the ensembles are over our domain, or how much
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

- Any scoring; that is 004–006.
- WN3 variables other than 2 m temperature.

## Open questions

- Access: the WeatherNext data request form must be filed and approved (5–7 business days), and a credential put in the cloud environment.
- Whether WN3 becomes a sixth canonical source on the HF dataset or stays local; the size decides.
