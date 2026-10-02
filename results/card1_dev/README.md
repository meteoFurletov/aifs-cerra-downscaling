# Card 1 on the development folds (provisional)

Output of `pipeline/score_stations.py --resample-stations --figure` on temporal folds 0–2 (one
summer, 2025-07-02 to 2025-09-12), 83 scored SYNOP stations, 2 Oct 2026. **Superseded:** the
confirmatory test on the sealed folds 3–12 ([card1_confirmatory](../card1_confirmatory/README.md))
does not confirm the headline below.

Model rows (prediction files built from the night's experiments, branch `night-experiments`,
`experiments/2026-10-02-night/`; not committed, ~45 MB each):

- `surface (40 km ring)`: bilinear + the surface model's systematic correction, held out in space.
  Each station's value comes from the model of its own spatial fold, trained only on cells
  farther than 40 km from every station of that fold and on tables from other temporal folds.
  The file is a composite: only station cells are meaningful (verified equal, to 0.0, to the
  held-out station predictions).
- `CNN v0`: the original 39k-parameter CNN's saved predictions (last epoch).
- `lookup own cell (not held out)`: bilinear + mean CERRA residual per cell × valid hour × lead.
  It uses CERRA at the station's own cell, which assimilated the station: a reference, not a claim.

Headline, dressed with the AIFS spread (like-for-like CRPS), 95 % intervals from `bootstrap.md`:
the surface model beats the raw AIFS ensemble in CRPS at every lead (+24 h: −0.043
[−0.073, −0.013]) and beats bilinear only at +0 h (RMSE −0.081 [−0.125, −0.040]).
