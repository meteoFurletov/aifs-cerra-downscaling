# AIFS → CERRA downscaling, Leningrad Oblast

Downscale ECMWF AIFS ENS 2 m temperature forecasts (0.25°) to the CERRA regional
reanalysis grid (5.5 km) over Leningrad Oblast and its lakes, and verify the result
against independent SYNOP station observations.

Moved out of Claude Science on 2026-09-24 (project "Downscaling of NWP for northwest
of Russia"). Every file the project held is here, sorted into folders. The one file
left behind is the saved Copernicus API key.

## Quick start

```bash
uv sync
uv run python -c "from dataset import check; print(check())"
```

All 15 checks should come back `True`; verified on 2026-09-24, about 40 seconds.

```python
from dataset import load_stage1, load_stage2, load_stations
d = load_stage2()            # AIFS -> CERRA pairs: X, Y, B, R, lead, fold, valid, ...
d = load_stage2(aux=True)    # + ERA5 lake, snow, skin-temperature and wind channels
d = load_stage1()            # ERA5 -> CERRA pairs
st, obs = load_stations()    # 299 stations, 717,034 observations
```

`dataset.py` reads from `./data` by default. Set `DOWNSCALING_DATA` to point elsewhere.
On a fresh clone, `./scripts/fetch_data.sh` pulls the five sources (~520 MB) from the
private HF dataset `meteof/aifs-cerra-downscaling-data`; Claude Code cloud sessions do
this automatically through the SessionStart hook in `.claude/settings.json`.

## Layout

| Folder | What | In git |
|---|---|---|
| `dataset.py` | The loader: builds every training set from the five source files | yes |
| `docs/` | `README.md` (project state), `DATA.md`, `COMPARISONS.md`, `GRIDS.md`, `MODEL.md`, roadmap. **Read `COMPARISONS.md` before quoting any RMSE** | yes |
| `pipeline/` | The scripts that built the data and trained the CNN | yes |
| `docs/estate.md`, `docs/balka/` | Balka's facts document and change artefacts (see `AGENTS.md`) | yes |
| `features/` | Gherkin scenarios, the contract for each change | yes |
| `scripts/` | `fetch_data.sh` / `publish_data.sh` (HF dataset sync), cloud-session hook | yes |
| `results/` | Result tables (CSV, JSON) | yes |
| `figures/` | Every figure, plus the interactive CERRA page | yes |
| `literature/` | Literature review, notes and citation tables. `pdf/` and `raw/` stay local | partly |
| `data/` | The five canonical sources (`cerra.npz`, `era5.npz`, `aifs.npz`, `stations.parquet`, `station_obs.parquet`), derived files, `raw/` GRIB downloads, `scratch/` intermediates | no, 15 GB |

`EXPORT_MANIFEST.json` lists every exported file with its size.

## Where it stands

- **Data phase complete.** All inputs, the target and the station truth are built and
  validated. See `docs/README.md`.
- **Deterministic baseline fitted.** A 39k-parameter CNN gains +0.09 °C over bilinear
  interpolation on held-out warm-season folds, almost all of it over Ladoga
  (+0.77 °C there, +0.05 °C over land). It is far too smooth: the next rung is a
  generative model. See `docs/MODEL.md`.
- **Related work.** Jua, "Universal Diffusion-Based Probabilistic Downscaling"
  (arXiv 2602.11893): the same ERA5 → CERRA setup at European scale, with a diffusion
  model applied zero-shot to AIFS and other forecasts.

## Next step

The comparison that paper did not make: the downscaled forecast against the **raw
AIFS ensemble**, scored at stations held out by location, per lead time. Target: a
public write-up by 31 October 2026.

## Notes

- The scripts in `pipeline/` were written for Claude Science's flat working folder.
  They read and write files in the current directory, so run them from the folder
  that holds their inputs, usually `data/` or `data/scratch/`.
- Fetching new data from Copernicus needs your own `~/.cdsapirc`.
- `data/raw/cerra_upload_*.grib` are the original CERRA downloads, 12.8 GB. CERRA
  cannot be cut to a region before download, so keep them.
