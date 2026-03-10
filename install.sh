#!/usr/bin/env bash
set -euo pipefail

echo "Installing DexOS..."

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required but not installed."
  exit 1
fi

python3 -m venv .venv
. .venv/bin/activate

python -m pip install --upgrade pip

mkdir -p state
touch state/runtime.jsonl
touch state/talnir_trace.jsonl
touch state/executor_decisions.jsonl
touch state/tool_results.jsonl

echo
echo "DexOS installation complete."
echo
echo "Run DexOS with:"
echo "  . .venv/bin/activate && python3 run_dex.py"
