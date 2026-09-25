# Estate

Owner: Nikita Furletov. The one place for the names and facts every stage reads before
drafting. A correction that lands in chat twice lands here once.

## Names

- **AIFS ENS**: ECMWF's AI *ensemble* forecast, 0.25°, the model input. Held as
  control, ensemble mean and spread per lead (`aifs.npz`), not as 51 members.
  Not "AIFS" alone, which also names the single deterministic model.
- **CERRA**: Copernicus regional reanalysis, 5.5 km Lambert grid, the target. It is
  the *truth* in comparison A and a *scored product* in comparison B.
- **ERA5**: global reanalysis, 0.25°. It is an analysis with no lead time: the stage-1
  input and AIFS's training data.
- **SYNOP**: station truth for 2025–26, raw WMO FM-12 bulletins from OGIMET. **ISD**
  is the 2015–24 archive of the same reports. **IEM** is METAR, a cross-check only.
- **Stage 1 / stage 2**: ERA5 → CERRA pairs / AIFS ENS → CERRA pairs
  (`load_stage1` / `load_stage2`).
- **Comparisons A, B, C**: gridded against CERRA / at stations 2025–26 / at stations
  2015–24. Defined in [COMPARISONS.md](COMPARISONS.md).
- **Target window / input crop**: the (123, 127) CERRA cells the model predicts / the
  (57, 116) 0.25° cells it sees. The domain is Leningrad Oblast plus a margin;
  St Petersburg is only the worked example in [GRIDS.md](GRIDS.md).
- **Station roles**: `target` (85, inside the target window) or `input_crop_only`
  (214). 83 target stations are `scored`.
- **Folds**: 13 temporal blocks of 21 days with 5-day gaps from `FOLD_EPOCH`
  2025-07-02, shared by both stages. Station spatial folds are `stations.fold`.
- **Stores**: code at GitHub `meteoFurletov/aifs-cerra-downscaling` (public); the five
  canonical sources at HF dataset `meteof/aifs-cerra-downscaling-data` (private).
- **Sibling**: `../improver-nw-russia`, the PhD post-processing core (IMPROVER over
  GEFS + AIFS). Separate repo; nothing here imports it.

## Facts

- Before quoting any score, read [COMPARISONS.md §6](COMPARISONS.md). Every number
  names its comparison and is reported per lead and season. Beating comparison A is
  not validation; station claims need the spatial holdout.
- [DATA.md §4](DATA.md) lists eleven traps that silently corrupt results. Read the one
  that touches a data path before changing it.
- `dataset.py` is the only way to build training sets. Nothing derived is stored;
  `check()` stays 15/15 `True`. Stage-2 rows are keyed by **(valid, lead)**.
- Local only: the 13 GB of raw CERRA GRIB (`data/raw/`), the Copernicus key
  (`~/.cdsapirc`), and the `pipeline/` scripts that rebuild sources or fetch new data.
- `pipeline/` scripts come from Claude Science's flat folder and read and write the
  current directory; run them from `data/` or `data/scratch/`. `dataset.py` and the
  docs still carry leftovers from it (`host` arguments, `{{artifact:...}}` links).
- Cloud sessions have no GPU. Their SessionStart hook runs `uv sync` and fetches the
  sources. Balka reaches them through the environment's setup script
  (`scripts/cloud_env_setup.sh`), because cloud sessions ignore `enabledPlugins`.
- Deadline: the public write-up (downscaled forecast against raw AIFS ENS, per lead,
  at stations held out by location) is due 31 October 2026.

## How changes land

- One repo, one branch per change, a pull request to `main`; Nikita merges.
- A change that rebuilds a canonical source runs `check()` to 15/15 first, then
  `scripts/publish_data.sh` after the merge. The HF dataset's commit history is the
  data's history; roll back by reverting that commit.
- The cloud environment's network list and setup script are edited by hand at
  claude.ai/code. Keep `scripts/cloud_env_setup.sh` in step with the setup script.
- Roll back code by reverting the pull request.
