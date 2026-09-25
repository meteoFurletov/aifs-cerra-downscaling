# AGENTS.md

Entry point for agent sessions on this repo. `README.md` has the project summary;
`docs/README.md` has the full state.

## What this project is

Downscaling ECMWF AIFS ENS 2 m temperature (0.25°) to the CERRA 5.5 km grid over
Leningrad Oblast, verified at held-out SYNOP stations. Data phase is closed; a
deterministic CNN baseline is fitted (`docs/MODEL.md`). Next: a generative model, and
scoring the downscaled forecast against the **raw AIFS ensemble** per lead time at
stations held out by location. Public write-up due 31 October 2026.

## Rules that prevent real errors

- **Read `docs/COMPARISONS.md` before quoting any RMSE/CRPS.** CERRA is the *truth*
  in the gridded comparison and a *scored product* in the station comparison. Every
  number must name its comparison.
- `docs/DATA.md` lists traps that silently corrupt results (SYNOP decoding, fold
  arithmetic, valid-time keys). Read the relevant one before touching a data path.
- `dataset.py` is the only way to build training sets. Nothing derived is stored;
  do not add pre-paired files to `data/`. `check()` must stay all-`True`.
- Stage-2 rows are keyed by **(valid, lead)**, not valid alone.

## Data

- `dataset.py` reads the five canonical sources from `data/` (or `$DOWNSCALING_DATA`):
  `cerra.npz`, `era5.npz`, `aifs.npz`, `stations.parquet`, `station_obs.parquet`
  (~520 MB). They live in the private HF dataset `meteof/aifs-cerra-downscaling-data`;
  `scripts/fetch_data.sh` pulls them (needs `HF_TOKEN`).
- Everything else in `data/` (13 GB raw CERRA GRIB, `scratch/`, derived files) exists
  only on Nikita's machine. Cloud sessions do not have it; `pipeline/` scripts that
  rebuild sources from GRIB or fetch from Copernicus are local-only.
- `pipeline/` scripts were written for Claude Science's flat folder: they read and
  write the current directory. Run them from `data/` or `data/scratch/`.

## Where work runs

- **Cloud sessions (Claude Code on the web):** loader, verification, analysis,
  small CPU models, docs, figures. The SessionStart hook runs `uv sync` and fetches
  data when `CLAUDE_CODE_REMOTE=true`. No GPU. Plugins (balka) come from the
  environment's setup script, recorded in `scripts/cloud_env_setup.sh`: cloud sessions
  ignore `enabledPlugins` in `.claude/settings.json`.
- **Local only:** Copernicus downloads (`~/.cdsapirc`), anything reading `data/raw/`.
- **GPU training** needs a GPU host; not set up yet.

## Conventions

- Python via `uv` (`uv run python ...`). Extras: `grib` for pipeline, `train` for torch.
- Anchor comments: `AICODE-NOTE:` / `AICODE-TODO:` / `AICODE-QUESTION:`; grep for
  existing `AICODE-` before scanning files.
- Docs still carry Claude Science leftovers (`host` arguments, `{{artifact:...}}`
  image links). Fix them when you touch a doc; don't mass-rewrite.
