#!/bin/sh
set -eu

release_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python_command=${PYTHON:-python3}

"$release_root/build_documents.sh"
"$python_command" "$release_root/tools/make_manifest.py"
"$release_root/reproduce.sh" "$@"

