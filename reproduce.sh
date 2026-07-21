#!/bin/sh
set -eu

release_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python_command=${PYTHON:-python3}
compiler_command=${CXX:-c++}
trial_count=100000
use_sanitizers=1

usage() {
  printf '%s\n' "usage: ./reproduce.sh [--trials N] [--no-sanitizers]"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --trials)
      [ "$#" -ge 2 ] || { usage >&2; exit 2; }
      trial_count=$2
      shift 2
      ;;
    --no-sanitizers)
      use_sanitizers=0
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      printf '%s\n' "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

case "$trial_count" in
  ''|*[!0-9]*)
    printf '%s\n' "--trials must be an integer of at least 2" >&2
    exit 2
    ;;
esac
[ "$trial_count" -ge 2 ] || {
  printf '%s\n' "--trials must be an integer of at least 2" >&2
  exit 2
}

command -v "$python_command" >/dev/null 2>&1 || {
  printf '%s\n' "Python 3 was not found: $python_command" >&2
  exit 1
}
command -v "$compiler_command" >/dev/null 2>&1 || {
  printf '%s\n' "A C++20 compiler was not found: $compiler_command" >&2
  exit 1
}

build_root=$(mktemp -d "${TMPDIR:-/tmp}/grand-coupling-release.XXXXXX")
cleanup() {
  rm -rf -- "$build_root"
}
trap cleanup EXIT HUP INT TERM

started_at=$(date +%s)
printf '%s\n' "Grand-coupling complete reproduction"
printf '%s\n' "release: $release_root"
printf '%s\n' "temporary build: $build_root"
printf '%s\n' "simulation trials per cell: $trial_count"
"$python_command" --version
"$compiler_command" --version

"$python_command" "$release_root/tools/verify_manifest.py"

printf '%s\n' "[1/8] exact six-state verification"
"$python_command" "$release_root/verification/verify_counterexample.py"

printf '%s\n' "[2/8] exact family verification"
"$python_command" "$release_root/verification/verify_family.py"

printf '%s\n' "[3/8] independent kernel-graph censuses"
"$python_command" "$release_root/verification/kernel_graph_census.py"
"$python_command" "$release_root/verification/classify_kernel_graphs.py"

printf '%s\n' "[4/8] independent C++ six-state verifier"
"$compiler_command" -std=c++20 -O2 -Wall -Wextra -Wpedantic \
  "$release_root/verification/verify_counterexample.cpp" \
  -o "$build_root/verify-counterexample"
"$build_root/verify-counterexample"

printf '%s\n' "[5/8] independent C++ family verifier"
"$compiler_command" -std=c++20 -O2 -Wall -Wextra -Wpedantic \
  "$release_root/verification/verify_family_independent.cpp" \
  -o "$build_root/verify-family"
"$build_root/verify-family"

printf '%s\n' "[6/8] exhaustive two-map lower-bound search"
"$compiler_command" -std=c++20 -O3 -Wall -Wextra -Wpedantic -DSTATE_COUNT=4 \
  "$release_root/verification/search_two_map_minimality.cpp" \
  -o "$build_root/search-two-map-n4"
"$build_root/search-two-map-n4"
"$compiler_command" -std=c++20 -O3 -Wall -Wextra -Wpedantic -DSTATE_COUNT=5 \
  "$release_root/verification/search_two_map_minimality.cpp" \
  -o "$build_root/search-two-map-n5"
"$build_root/search-two-map-n5"

printf '%s\n' "[7/8] memory-safety and undefined-behavior checks"
if [ "$use_sanitizers" -eq 1 ]; then
  "$compiler_command" -std=c++20 -O1 -g -Wall -Wextra -Wpedantic \
    -fsanitize=address,undefined -fno-omit-frame-pointer \
    "$release_root/verification/verify_counterexample.cpp" \
    -o "$build_root/verify-counterexample-sanitized"
  "$build_root/verify-counterexample-sanitized"
  "$compiler_command" -std=c++20 -O1 -g -Wall -Wextra -Wpedantic \
    -fsanitize=address,undefined -fno-omit-frame-pointer \
    "$release_root/verification/verify_family_independent.cpp" \
    -o "$build_root/verify-family-sanitized"
  "$build_root/verify-family-sanitized"
else
  printf '%s\n' "REDUCED VERIFICATION: sanitizers were explicitly disabled."
fi

printf '%s\n' "[8/8] deterministic properties, exact stationarity, and simulation smoke tests"
"$python_command" "$release_root/experiments/experiment_suite.py" --trials "$trial_count"

finished_at=$(date +%s)
elapsed_seconds=$((finished_at - started_at))
printf '%s\n' "Complete reproduction: PASS (${elapsed_seconds}s)"

