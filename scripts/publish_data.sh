#!/usr/bin/env bash
# One-off / on change: upload the five canonical sources to the private HF dataset.
# Run locally after `uvx --from huggingface_hub hf auth login` (token with write access).
set -euo pipefail

REPO="${DOWNSCALING_HF_REPO:-meteof/aifs-cerra-downscaling-data}"
SRC="$(cd "$(dirname "$0")/.." && pwd)/data"
FILES=(cerra.npz era5.npz aifs.npz stations.parquet station_obs.parquet DATA_MANIFEST.csv)

include=()
for f in "${FILES[@]}"; do
  [ -s "$SRC/$f" ] || { echo "publish_data: missing $SRC/$f" >&2; exit 1; }
  include+=(--include "$f")
done

# --private creates the dataset as private if it does not exist yet
uvx --from huggingface_hub hf upload "$REPO" "$SRC" . "${include[@]}" \
  --repo-type dataset --private --commit-message "Update canonical sources"
