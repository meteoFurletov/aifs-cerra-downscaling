# Estate

Owner: Nikita Furletov. The one place for the names and facts every stage reads before
drafting. A correction that lands in chat twice lands here once.

## Names

- **AIFS ENS**: ECMWF's AI *ensemble* forecast, 0.25°, the model input. Held as
  control, ensemble mean and spread per lead (`aifs.npz`), not as 51 members.
  Not "AIFS" alone, which also names the single deterministic model.
- **WeatherNext 3 (WN3)**: Google DeepMind's AI ensemble forecast, 64 members; runs at
  00/06/12/18 UTC go 15 days, the hourly runs between them 48 h. 2 m temperature on a 0.05°
  grid, calibrated to stations. A model
  compared alongside AIFS ENS, not an input. Zarr in GCS: all members at
  `gs://weathernext3_spatial/weathernext_3_0_0/zarr/` (Requester Pays), mean and
  percentiles at `gs://weathernext3_statistics_spatial/weathernext_3_0_0_statistics/zarr/`.
  The access granted on 2026-10-02 covers `wn3-reader`. Layout and size are under Facts.
- **Station head**: a network fitted to SYNOP observations that predicts at any point from
  forecast fields and local geography, after WN3's method (Rasp et al. 2026, arXiv 2609.03582).
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
- **WN3 access**: service account `wn3-reader@claude-cloud-meteof-weather.iam.gserviceaccount.com`
  in Google Cloud project `claude-cloud-meteof-weather`, the billing project for Requester
  Pays reads; the statistics need none. Its billing account is a Free Trial, linked
  2026-10-02: $300 for 90 days, never charged unless upgraded to a paid account, and the
  project stops when the credit or the days run out. The key and the billing project are
  the secrets `WN3_GCP_KEY_JSON` and `WN3_BILLING_PROJECT`.
- **Infisical**: the secrets store, Infisical Cloud (app.infisical.com). This repo's secrets
  are in project `weather`, environment `dev`; `.infisical.json` names the project.
- **Sibling**: `../improver-nw-russia`, the PhD post-processing core (IMPROVER over
  GEFS + AIFS). Separate repo; nothing here imports it.

## Facts

- WN3 layout (read 2026-10-02): both stores in GCS region us-east1, one Zarr per run,
  hourly from 2026-01-01 on; 2024–25 is still being backfilled. Leads run +1 h to +360 h:
  **there is no lead 0**. 2 m temperature comes raw at 0.1° (`temperature_2m`) and
  station-calibrated at 0.05° (`station_head_temperature_2m`). An all-members chunk is one
  member × 6 h of leads × the whole globe: ~118 MB at 0.1°, ~470 MB at 0.05°. So one lead,
  all members, one run is ~7.6 GB or ~30 GB, whatever the domain. The statistics hold
  `_mean` and `_p10`…`_p90` of both, chunked one lead × the globe.
- WN3 licence: download only runs whose whole 15-day window ended more than 1 h ago.
  Everything held is then CC BY 4.0: credit "WeatherNext 3, Google DeepMind", link the
  licence and say what was changed. Newer data falls under the GDM Real-Time Experimental
  Data Terms of Use (sharing limits, a set citation text, revocable); keep none of it.
- Before quoting any score, read [COMPARISONS.md §6](COMPARISONS.md). Every number
  names its comparison and is reported per lead and season. Beating comparison A is
  not validation; station claims need the spatial holdout.
- [DATA.md §4](DATA.md) lists eleven traps that silently corrupt results. Read the one
  that touches a data path before changing it.
- `dataset.py` is the only way to build training sets. Nothing derived is stored;
  `check()` stays 15/15 `True`. Stage-2 rows are keyed by **(valid, lead)**.
- AIFS ENS v1 ran operationally until 2026-05-12, v2 since. `aifs.npz` holds 39 v2 inits
  (2026-05-12 to 05-31), most of temporal fold 12 (valid 2026-05-10 to 05-30); report that
  fold apart when the version could matter.
- Local only: the 13 GB of raw CERRA GRIB (`data/raw/`) and the Copernicus key
  (`~/.cdsapirc`), so the `pipeline/` scripts that rebuild sources or fetch new data
  run locally only.
- `pipeline/` scripts come from Claude Science's flat folder and read and write the
  current directory; run them from `data/` or `data/scratch/`. `dataset.py` (optional
  `host` argument) and `fetch_aifs_overlap.py` (`kernel` import) still carry leftovers
  from it.
- Cloud sessions have no GPU. Their SessionStart hook runs `uv sync` and fetches the
  sources. Balka reaches them through the environment's setup script
  (`scripts/cloud_env_setup.sh`), because cloud sessions don't install plugins from
  `enabledPlugins`. Once it is installed, `claude plugin list` shows balka twice (user
  and project scope): the same install, harmless.
- Secrets come from Infisical only, never from a file or the repo. Locally, wrap the
  command: `infisical run --env=dev -- <command>`. In cloud sessions the environment holds
  only the machine identity (`INFISICAL_CLIENT_ID`, `INFISICAL_CLIENT_SECRET`), and the
  SessionStart hook passes the secrets to every Bash command. WN3 reads there need
  `app.infisical.com`, `oauth2.googleapis.com` and `storage.googleapis.com` on the network
  allowlist. `infisical secrets` prints values in clear; check one through `infisical run`.
- Deadline: the public write-up (downscaled forecast against raw AIFS ENS, per lead,
  at stations held out by location) is due 31 October 2026.

## How changes land

- One repo, one branch per change, a pull request to `main`; Nikita merges.
- Balka intents are research changes only. Setup, tooling and cleanup go on their own
  branch and pull request, outside `balka/`; `plan-sync` allows that, because no
  plan on such a branch is `accepted`.
- A change that rebuilds a canonical source runs `check()` to 15/15 first, then
  `scripts/publish_data.sh` after the merge. The HF dataset's commit history is the
  data's history; roll back by reverting that commit.
- The cloud environment's network list and setup script are edited by hand at
  claude.ai/code. Keep `scripts/cloud_env_setup.sh` in step with the setup script.
- Roll back code by reverting the pull request.
