# Card 1 on the sealed folds 3–12 (confirmatory)

Output of `pipeline/score_stations.py --folds 3 4 5 6 7 8 9 10 11 12 --unlock-test
--resample-stations --by tfold --figure`, run once on 2 Oct 2026 by `MORNING.sh` (branch
`night-experiments`, `experiments/2026-10-02-night/night/`, unchanged since its 03:21 snapshot).
83 scored SYNOP stations, valid 2025-09-18 to 2026-05-30: autumn, winter and spring. Model rows
as in [card1_dev](../card1_dev/README.md); the 40 km ring is the primary claim, fixed before
these folds were scored.

Headline, dressed with the AIFS spread (like-for-like CRPS), 95 % intervals from `bootstrap.md`:

- The surface model does **not** beat the raw AIFS ensemble in CRPS at any lead (+0 h: +0.006
  [−0.022, 0.033]; +168 h: −0.011 [−0.029, 0.004]).
- It is **worse** than bilinear at +0 to +72 h (CRPS +0.037 [0.018, 0.056] at +0 h, +0.016
  [0.002, 0.031] at +72 h) and level at +120 and +168 h.
- Bilinear beats the raw AIFS ensemble at every lead (CRPS −0.031 [−0.049, −0.013] at +0 h,
  −0.014 [−0.024, −0.005] at +168 h): interpolation, which the raw nearest-cell Gaussian lacks.

The dev-fold headline in `card1_dev` (one summer) does not hold over autumn to spring. Fold 12
(valid 2026-05-10 to 05-30) is mostly AIFS ENS v2, which replaced v1 on 2026-05-12; `tables.md`
reports it per fold.
