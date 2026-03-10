# DexOS

DexOS is an autonomous AI runtime that evaluates system state, reasons about direction using Talnir, chooses a continuation path, executes tools, and preserves continuity across runtime cycles.

## Core Loop
tick
→ snapshot
→ ☧ state
→ 🦅 Talnir interpretation
→ 🜇 continuation decision
→ executor selects mode
→ tool execution
→ runtime logging
→ Talnir realignment
→ next state


## Quick Install
git clone https://github.com/zech-dexos/dexos

cd dexos
./install.sh


## Run DexOS

. .venv/bin/activate
python3 run_dex.py


## Demo

DexOS demonstrates:

- stateful runtime snapshots
- Talnir reasoning
- continuation decisions
- mode switching
- tool execution
- goal progression
- runtime logging
