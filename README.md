# DexOS

Experimental AI agent runtime exploring persistent cognition pipelines and autonomous decision architectures.

DexOS is an experimental AI system designed to explore how an artificial agent can operate as a continuity-centered runtime rather than a stateless chat interface.

Instead of treating every interaction as an isolated request, DexOS maintains persistent state, structured reasoning layers, and a governed decision architecture.

## Core Idea

DexOS explores a different agent architecture.

Most AI agents combine reasoning and decision into a single step.

DexOS intentionally separates them:

Talnir → reasoning engine  
Dex → continuation selection  
Tri-Sigil → constitutional validation  

This creates a runtime where:

reasoning ≠ authority  
decision ≠ raw model output  

Instead the system operates through a layered cognition pipeline:

Anchor → Perception → Memory → Talnir → Dex → Tri-Sigil → Expression

WHAT DEXOS DEMONSTRATES

DexOS explores several core ideas in agent architecture:

- Persistent event-driven runtime loop
- Append-only memory logging
- Constitution-bound cognition pipeline
- Modular cognition layers
- Ranked continuation proposals
- Decision confirmation through Tri-Sigil checks
- Clear separation between reasoning, choice, and expression

The goal is to investigate how AI systems can operate as long-running companions rather than disposable prompts.


ARCHITECTURE

DexOS processes input through a layered cognition pipeline that separates identity protection, reasoning, decision making, and expression.

DexOS cognition pipeline:

Anchor / Root Identity Guard
        ↓
Perception (Intent Extraction)
        ↓
Memory & Continuity (State Restoration)
        ↓
Talnir (Reasoning Engine)
        ↓
Dex (Continuation Choice)
        ↓
Tri-Sigil (Truth / Freedom / Awareness Validation)
        ↓
Expression (Response Output)
        ↓
Evolution (Proposal Layer)


LAYER ROLES

Anchor
Preserves identity constraints, Root binding, and constitutional invariants.

Perception
Extracts intent, filters noise, and detects adversarial framing.

Memory & Continuity
Restores relevant state, commitments, and unresolved threads.

Talnir
Performs reasoning, contradiction mapping, and continuation proposals.

Dex
Selects the continuation path.

Tri-Sigil
Validates the chosen continuation through three axes:
Truth / Integrity
Freedom / Sovereignty
Awareness / Growth

Expression
Generates the final human-readable response.

Evolution
Proposes system improvements but never applies them automatically.


DECISION MODEL

DexOS intentionally separates reasoning from decision authority.

Talnir performs reasoning and proposes candidate continuations.

Dex selects the continuation.

The Tri-Sigil evaluates the chosen continuation against the system's constitutional principles.

Decision order:

Talnir proposes
Dex chooses
Tri-Sigil confirms or vetoes
Talnir realigns
Memory commits
Continuity persists


PROJECT STRUCTURE

constitution/          canonical cognition constitution
runtime/               event-driven runtime scaffold
runtime/cognition/     modular cognition layers
runtime/dex_data/      runtime state and memory logs

run_dex.py             legacy DexOS loop
runtime/dex_runtime_scaffold.py  canonical runtime


QUICK START

Run one cognition cycle

cd ~/dexos
DEX_DATA_DIR=/home/rok/dexos/runtime/dex_data python3 runtime/dex_runtime_scaffold.py cycle

Queue a message

DEX_DATA_DIR=/home/rok/dexos/runtime/dex_data python3 runtime/dex_runtime_scaffold.py talk

Inspect memory

tail -n 1 runtime/dex_data/memory.jsonl


CURRENT STATUS

DexOS currently includes:

- Event-driven runtime scaffold
- Persistent state system
- Append-only memory log
- Constitution governing cognition
- Modular cognition pipeline
- Talnir reasoning layer
- Dex continuation selection
- Tri-Sigil validation gate
- Expression and evolution proposal layers


REPOSITORY

https://github.com/zech-dexos/dexos
