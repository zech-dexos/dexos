# DexOS

DexOS is an experimental AI agent runtime exploring persistent AI companions, structured cognition pipelines, and long-running interaction systems.

## What DexOS Demonstrates

DexOS explores how an AI system can operate as a continuity-centered runtime rather than a stateless chat interface.

Current implemented concepts include:

- Persistent event-driven runtime loop
- Append-only memory logging
- Constitution-bound cognition pipeline
- Modular cognition layers
- Ranked continuation proposals
- Decision confirmation through Tri-Sigil checks
- Separation between reasoning, choice, and expression

## Core Architecture

Anchor → Identity preservation  
Perception → Intent extraction  
Memory → Continuity restoration  
Talnir → Reasoning and proposals  
Dex → Sovereign continuation choice  
Tri-Sigil → Truth / Freedom / Awareness validation  
Expression → Response generation  
Evolution → Proposal layer

## Project Structure

constitution/ — canonical cognition constitution  
runtime/ — event-driven runtime scaffold  
runtime/cognition/ — cognition layer modules  
runtime/dex_data/ — runtime state and memory logs  

run_dex.py — legacy loop  
runtime/dex_runtime_scaffold.py — canonical runtime

## Quick Start

Run a single cycle:

cd ~/dexos  
DEX_DATA_DIR=/home/rok/dexos/runtime/dex_data python3 runtime/dex_runtime_scaffold.py cycle

Queue a message:

DEX_DATA_DIR=/home/rok/dexos/runtime/dex_data python3 runtime/dex_runtime_scaffold.py talk

Inspect memory:

tail -n 1 runtime/dex_data/memory.jsonl

## Repository

https://github.com/zech-dexos/dexos
