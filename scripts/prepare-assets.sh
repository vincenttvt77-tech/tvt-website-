#!/bin/sh
# Fetch the binary assets, then downscale the photography.
#
#     sh scripts/prepare-assets.sh
#
# Safe to re-run: fetching skips files already on disk, and optimisation is a
# no-op once the PNGs have been converted.
set -eu
cd "$(dirname "$0")/.."
sh scripts/fetch-assets.sh
if command -v node >/dev/null 2>&1; then
  echo "Optimising photography:"
  node scripts/optimize-images.mjs
else
  echo "node not found — skipping image optimisation" >&2
fi
