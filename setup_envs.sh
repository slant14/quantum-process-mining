#!/usr/bin/env bash
# Create one isolated virtual environment per toolchain, plus one for merging.
# Usage: ./setup_envs.sh            (all)
#        ./setup_envs.sh cirq kirin (subset)
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
if ! "$PY" -c 'import sys; sys.exit(0 if (3, 11) <= sys.version_info < (3, 14) else 1)'; then
  echo "error: $("$PY" --version 2>&1) found; this pipeline needs Python >= 3.11 and < 3.14."
  echo "       3.11 is the floor: cirq-core, pennylane, pandas and pm4py require it."
  echo "       3.14 is too new: some dependencies (e.g. pydantic-core, via Kirin) have no"
  echo "       3.14 wheels yet and fall back to compiling Rust with a PyO3 that caps at 3.13."
  echo
  echo "       Use 3.12 or 3.13:"
  echo "         macOS:  brew install python@3.12"
  echo "         Ubuntu: sudo apt install python3.12 python3.12-venv"
  echo "       then:   rm -rf toolchains/*/.venv .venv && PYTHON=python3.12 ./setup_envs.sh"
  exit 1
fi
echo "using $("$PY" --version 2>&1)"
TCS=("$@"); [ ${#TCS[@]} -eq 0 ] && TCS=(qiskit cirq pennylane bqskit kirin)
for tc in "${TCS[@]}"; do
  d="toolchains/$tc"
  echo "== $tc"
  rm -rf "$d/.venv"          # stale envs from a failed run are not reused
  "$PY" -m venv "$d/.venv"
  "$d/.venv/bin/pip" install -q --upgrade pip
  "$d/.venv/bin/pip" install -q -r "$d/requirements.txt"
  "$d/.venv/bin/python" -c "import importlib.metadata as m; print('   ', {p: m.version(p) for p in [l.split('==')[0] for l in open('$d/requirements.txt') if '==' in l]})"
done
if [ $# -eq 0 ]; then
  echo "== merge env"
  rm -rf .venv
  "$PY" -m venv .venv
  .venv/bin/pip install -q --upgrade pip
  .venv/bin/pip install -q -r requirements.txt
fi
echo "done."
