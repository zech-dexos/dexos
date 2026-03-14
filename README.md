# DexOS

DexOS is an autonomous AI runtime that evaluates system state, reasons about direction using Talnir, chooses a continuation path, executes tools, and preserves continuity across runtime cycles.

## What DexOS Demonstrates

DexOS is an experimental AI agent runtime exploring how AI systems can operate with continuity, reflection, and long-running interaction.

Key architecture components:

- Persistent AI runtime loop
- Event-driven interaction model
- Append-only memory system for interaction history
- Layered cognition pipeline  
  *(Perception → Memory → Reasoning → Decision → Expression)*
- Talnir reasoning framework for structured reflection
- Continuation-based decision architecture
- Agent execution modes for reflective and task-focused cycles

DexOS explores how AI systems can maintain coherent identity, memory continuity, and agent-style behaviors beyond stateless chat interfaces.

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
