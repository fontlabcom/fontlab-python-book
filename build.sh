#!/bin/sh
# this_file: build.sh
set -eu
cd "$(dirname "$0")"
exec sh src_docs/build.sh "$@"
