#!/bin/sh
# Materialise the binary assets the site references.
#
# They are not committed: the original brand PNGs live on the existing
# deployment, and the photography was generated and is served from a CDN.
# Run this once locally (or let the deploy build run it) to populate assets/.
#
#     sh scripts/fetch-assets.sh
#
# Once the files are on disk, commit them — then this script is only needed
# when the artwork changes.

set -eu
cd "$(dirname "$0")/.."
mkdir -p assets assets/img

BRAND_SRC="${BRAND_SRC:-https://tvt-capital.vercel.app/assets}"
CDN="https://d8j0ntlcm91z4.cloudfront.net/user_3Bgs2ORcT6Frbqv7AKCyBALqQRm"

get() { # url, destination
  if [ -s "$2" ]; then
    echo "  have  $2"
    return 0
  fi
  if curl -sSLf -o "$2.tmp" "$1"; then
    mv "$2.tmp" "$2"
    echo "  got   $2 ($(wc -c < "$2") bytes)"
  else
    rm -f "$2.tmp"
    echo "  MISS  $2  <- $1" >&2
    return 1
  fi
}

echo "Brand marks (original artwork):"
get "$BRAND_SRC/tvt-logo.png"         assets/tvt-logo.png
get "$BRAND_SRC/favicon-32.png"       assets/favicon-32.png
get "$BRAND_SRC/favicon-64.png"       assets/favicon-64.png
get "$BRAND_SRC/apple-touch-icon.png" assets/apple-touch-icon.png

echo "Photography:"
get "$CDN/hf_20260824_164923_509aeff4-9a68-4fa5-8134-c5ca0f996f1e.png" assets/img/facade.png
get "$CDN/hf_20260824_164923_6e575394-3a5f-4c4f-b863-3460ede00fdb.png" assets/img/boardroom.png
get "$CDN/hf_20260824_164923_bf84988e-e499-4554-a0cf-c6c77277f697.png" assets/img/engraving.png
get "$CDN/hf_20260824_164923_acc7f9ac-c8b4-47ad-940c-1b768a5cab0c.png" assets/img/ledger.png

echo "Done."
