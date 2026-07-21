#!/bin/sh
set -eu

release_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python_command=${PYTHON:-python3}

command -v "$python_command" >/dev/null 2>&1 || {
  printf '%s\n' "Python 3 was not found: $python_command" >&2
  exit 1
}

"$python_command" -c "import reportlab, pypdf; print('ReportLab', reportlab.Version, '| pypdf', pypdf.__version__)" || {
  printf '%s\n' "Install the pinned document dependencies with:" >&2
  printf '%s\n' "  python3 -m pip install -r requirements-docs.txt" >&2
  exit 1
}

"$python_command" "$release_root/paper/build_paper.py"
"$python_command" "$release_root/audit/build_verification.py"
"$python_command" "$release_root/tools/qa_pdfs.py"
printf '%s\n' "Document build and structural PDF checks: PASS"

