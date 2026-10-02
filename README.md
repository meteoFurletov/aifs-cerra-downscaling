# AIFS → CERRA downscaling, Leningrad Oblast

Downscale ECMWF AIFS ENS 2 m temperature forecasts (0.25°) to the CERRA regional
reanalysis grid (5.5 km) over Leningrad Oblast and its lakes, and verify the result
against independent SYNOP station observations.

Moved out of Claude Science on 2026-09-24 (project "Downscaling of NWP for northwest
of Russia"). Every file the project held was moved to the owner's checkout; the public
repo carries the code, docs, results and figures, not the data (see [Layout](#layout)).

## Quick start

```bash
uv sync
./scripts/fetch_data.sh    # the five data sources, ~520 MB; needs access, see below
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
`fetch_data.sh` pulls from the HF dataset `meteof/aifs-cerra-downscaling-data`, which is
private, so it works only for the owner; Claude Code cloud sessions run it through the
SessionStart hook in `.claude/settings.json`.

**Without access**, rebuild the sources from their providers (see
[Data and credits](#data-and-credits)): CERRA and ERA5 from the Copernicus Climate Data
Store with your own key in `~/.cdsapirc`, AIFS ENS from dynamical.org, SYNOP from OGIMET.
The `pipeline/` scripts hold the retrieval, decoding and cropping steps, and
`docs/DATA.md` §2 says what each source costs: CERRA cannot be cut to a region, so a year
is 6.7 GB downloaded for 0.17 GB kept. Three gaps remain: ERA5 has no committed request
(`docs/README.md` §5 gives its area), `fetch_aifs_overlap.py` opens the store through a
Claude Science helper that is not in this repo, and no committed script packs the outputs
into the five files. `fetch_cerra_target.py` asks for 2015–24; set its `YEARS` for
2025–26.

## Layout

| Folder | What | In git |
|---|---|---|
| `dataset.py` | The loader: builds every training set from the five source files | yes |
| `docs/` | `README.md` (project state), `DATA.md`, `COMPARISONS.md`, `GRIDS.md`, `MODEL.md`, roadmap. **Read `COMPARISONS.md` before quoting any RMSE** | yes |
| `pipeline/` | The scripts that built the data and trained the CNN | yes |
| `balka/`, `docs/estate.md` | Balka's change artefacts and facts document (see `AGENTS.md`) | yes |
| `features/` | Gherkin scenarios, the contract for each change. Created by the first balka spec | not yet |
| `scripts/` | `fetch_data.sh` / `publish_data.sh` (HF dataset sync), cloud-session hook | yes |
| `results/` | Result tables (CSV, JSON) | yes |
| `figures/` | Every figure, plus the interactive CERRA page | yes |
| `literature/` | Literature review, notes and citation tables. `pdf/` and `raw/` stay local | partly |
| `data/` | The five canonical sources (`cerra.npz`, `era5.npz`, `aifs.npz`, `stations.parquet`, `station_obs.parquet`), derived files, `raw/` GRIB downloads, `scratch/` intermediates | only `domain_spec_leningrad.json` and `DATA_MANIFEST.csv`; the rest is 15 GB |

`EXPORT_MANIFEST.json` lists every exported file with its size.

## Where it stands

- **Data phase complete.** All inputs, the target and the station truth are built and
  validated. See `docs/README.md`.
- **Deterministic baseline fitted.** In comparison A (gridded, CERRA as truth; see
  `docs/COMPARISONS.md`) a 39k-parameter CNN gains +0.085 °C over bilinear
  interpolation at its last epoch on held-out warm-season folds 0–2, pooled over leads
  (+0.11 °C at +0 h to +0.07 °C at +168 h). The gain is largest over water: +0.34 °C
  over open water against +0.05 °C over land. The +0.090 °C in
  `results/cnn_results.json` and the `docs/MODEL.md` figure is the best of four
  checkpoints, picked on the test fold itself. At stations (comparison B, a provisional
  first pass not yet committed: nearest cell, the same folds, not held out by location)
  it does not beat bilinear at five of six leads. It is far too smooth: the next rung is
  a generative model. See `docs/MODEL.md`.
- **Against the raw AIFS ensemble at held-out stations** (comparison B, sealed folds
  3–12, autumn to spring, scored once on 2 Oct 2026): a correction learned from CERRA
  (the surface model, held out by a 40 km ring) does not beat the raw ensemble in CRPS at
  any lead, and is worse than bilinear at +0 to +72 h. Bilinear interpolation beats the
  raw nearest-cell ensemble at every lead. The summer gains on the dev folds did not
  hold. See [`results/card1_confirmatory`](results/card1_confirmatory/README.md).
- **Related work.** Jua, "Universal Diffusion-Based Probabilistic Downscaling"
  (arXiv 2602.11893): the same ERA5 → CERRA setup at European scale, with a diffusion
  model applied zero-shot to AIFS and other forecasts.

## Next step

The public write-up of the comparison above, by 31 October 2026.

## Notes

- The scripts in `pipeline/` were written for Claude Science's flat working folder.
  They read and write files in the current directory, so run them from the folder
  that holds their inputs, usually `data/` or `data/scratch/`.
- `data/raw/cerra_upload_*.grib` are the original CERRA downloads, 12.8 GB. CERRA
  cannot be cut to a region before download, so keep them.

## Data and credits

The repo holds code, results and figures; the data sources themselves are not
redistributed.

- **CERRA** and **ERA5**: Copernicus Climate Change Service (C3S) Climate Data Store,
  CC BY 4.0. CERRA single levels, doi:[10.24381/cds.622a565a](https://doi.org/10.24381/cds.622a565a);
  ERA5 single levels, doi:[10.24381/cds.adbb2d47](https://doi.org/10.24381/cds.adbb2d47).
  Contains modified Copernicus Climate Change Service information 2026. Neither the
  European Commission nor ECMWF is responsible for any use that may be made of the
  Copernicus information or data it contains.
- **AIFS ENS**: ECMWF AIFS ENS forecast data processed by dynamical.org from ECMWF Open
  Data, doi:[10.5281/zenodo.18777399](https://doi.org/10.5281/zenodo.18777399).
  © 2026 European Centre for Medium-Range Weather Forecasts (ECMWF),
  [www.ecmwf.int](https://www.ecmwf.int), published under
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) and the
  [ECMWF Terms of Use](https://apps.ecmwf.int/datasets/licences/general/).
  Modified here: cropped, reduced to control, ensemble mean and spread, and interpolated.
  ECMWF does not accept any liability whatsoever for any error or omission in the data,
  their availability, or for any loss or damage arising from their use.
- **SYNOP**: WMO FM-12 reports from 299 stations in Russia, Finland (including Åland),
  Estonia, Latvia, Sweden, Lithuania and Belarus, retrieved through
  [OGIMET](https://www.ogimet.com). The reports are the copyright of the
  national services that issue them, subject to WMO Resolution 40.
- Also used: NOAA NCEI's Integrated Surface Database (ISD) for the 2015–24 station
  archive and comparison C, and the Iowa Environmental Mesonet (IEM, Iowa State
  University) as a METAR cross-check.

## Licence

The code is under the [MIT licence](LICENSE). The data keep their own licences, above.
