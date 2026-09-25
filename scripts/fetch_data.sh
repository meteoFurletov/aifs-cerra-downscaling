#!/usr/bin/env bash
# Pull the five canonical source files from the private HF dataset into data/.
# Auth: HF_TOKEN, a local `hf auth login`, or (cloud sessions) an API credential the
# egress proxy injects for huggingface.co. Skips files already present, so reruns are cheap.
set -euo pipefail

REPO="${DOWNSCALING_HF_REPO:-meteof/aifs-cerra-downscaling-data}"
DEST="${DOWNSCALING_DATA:-$(cd "$(dirname "$0")/.." && pwd)/data}"
FILES=(cerra.npz era5.npz aifs.npz stations.parquet station_obs.parquet)

missing=()
for f in "${FILES[@]}"; do [ -s "$DEST/$f" ] || missing+=("$f"); done
if [ ${#missing[@]} -eq 0 ]; then
  echo "fetch_data: all ${#FILES[@]} sources present in $DEST"
  exit 0
fi

mkdir -p "$DEST"
echo "fetch_data: downloading ${missing[*]} from $REPO"
uvx --from huggingface_hub hf download "$REPO" "${missing[@]}" \
  --repo-type dataset --local-dir "$DEST" --quiet >/dev/null
echo "fetch_data: done"
