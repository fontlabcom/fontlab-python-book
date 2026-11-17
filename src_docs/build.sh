#!/bin/sh
# this_file: src_docs/build.sh
set -eu
cd "$(dirname "$0")/.."
: "${SOURCE_DATE_EPOCH:=0}"
export SOURCE_DATE_EPOCH
exec uv run --project . python -m properdocs build --strict --clean \
  -f src_docs/mkdocs.yml "$@"
