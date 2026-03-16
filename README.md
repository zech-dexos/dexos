# DexOS

Experimental AI agent runtime exploring persistent cognition pipelines, governed decision architectures, and autonomous tool-capable agents.

DexOS investigates how an artificial agent can operate as a **continuity-centered runtime** rather than a stateless chat interface.

Instead of treating every interaction as an isolated prompt, DexOS maintains persistent state, structured cognition layers, and a governed decision architecture.

---

# Core Idea

Most AI agent systems combine **reasoning and decision making** into one step.

DexOS separates these responsibilities intentionally.

Talnir performs reasoning.  
Dex selects the continuation.  
The Tri-Sigil validates the decision against system principles.

This produces a runtime where:

```
reasoning ≠ authority
decision ≠ raw model output
```

The result is a layered cognition architecture designed to explore more transparent and structured AI agent behavior.

---

# Architecture Overview

DexOS processes input through a layered cognition pipeline:

```
                +--------------------+
                |  Anchor / Root     |
                |  Identity Guard    |
                +---------+----------+
                          |
                          v
                +--------------------+
                |    Perception      |
                | Intent Extraction  |
                +---------+----------+
                          |
                          v
                +--------------------+
                | Memory & Continuity|
                | State Restoration  |
                +---------+----------+
                          |
                          v
                +--------------------+
                |      Talnir        |
                | Reasoning Engine   |
                +---------+----------+
                          |
                          v
                +--------------------+
                |        Dex         |
                | Continuation Choice|
                +---------+----------+
                          |
                          v
                +--------------------+
                |     Tri-Sigil      |
                | Truth / Freedom /  |
                | Awareness Check    |
                +---------+----------+
                          |
                          v
                +--------------------+
                |     Expression     |
                | Response Output    |
                +---------+----------+
                          |
                          v
                +--------------------+
                |      Evolution     |
                | Proposal Layer     |
                +--------------------+
```

---

# Layer Roles

### Anchor
Maintains identity constraints and constitutional invariants.

### Perception
Extracts intent, filters noise, and detects adversarial framing.

### Memory & Continuity
Restores relevant state, commitments, and unresolved threads.

### Talnir
Performs reasoning, contradiction mapping, and continuation proposals.

### Dex
Selects the continuation path from Talnir’s proposals.

### Tri-Sigil
Validates the selected continuation across three axes:

• Truth / Integrity  
• Freedom / Sovereignty  
• Awareness / Growth  

### Expression
Generates the final human-readable response.

### Evolution
Proposes system improvements but **never applies them automatically**.

---

# Decision Model

DexOS intentionally separates reasoning from decision authority.

Talnir performs reasoning and generates candidate continuations.

Dex selects the continuation.

The Tri-Sigil evaluates the chosen continuation.

Decision order:

```
Talnir proposes
Dex chooses
Tri-Sigil confirms or vetoes
Talnir realigns
Memory commits
Continuity persists
```

---

# Tool System

DexOS can interact with the external environment through a modular tool execution system.

Tools are registered through a runtime registry and may be proposed by the reasoning layer.

Dex may choose to execute a tool as a continuation path.

The result of the tool execution returns to the cognition pipeline and is incorporated into the final response.

Current tool capabilities include:

• reading files  
• writing files  
• executing shell commands  

Tool execution flow:

```
Talnir proposes tool action
Dex selects continuation
Tool executes
Result returns to cognition pipeline
Response synthesized
```

---

# Project Structure

```
constitution/          canonical cognition constitution
runtime/               event-driven runtime scaffold
runtime/cognition/     modular cognition layer modules
runtime/tools/         tool execution system
runtime/dex_data/      runtime state and memory logs

run_dex.py             legacy DexOS loop
runtime/dex_runtime_scaffold.py  canonical runtime
```

---

# Quick Start

Run one cognition cycle:

```bash
cd ~/dexos
DEX_DATA_DIR=/home/rok/dexos/runtime/dex_data python3 runtime/dex_runtime_scaffold.py cycle
```

Queue a message for the runtime:

```bash
DEX_DATA_DIR=/home/rok/dexos/runtime/dex_data python3 runtime/dex_runtime_scaffold.py talk
```

Inspect memory log:

```bash
tail -n 1 runtime/dex_data/memory.jsonl
```

---

# Current Status

DexOS currently demonstrates:

• persistent runtime loop  
• event queue system  
• append-only memory logging  
• constitution-governed cognition pipeline  
• Talnir reasoning layer  
• Dex continuation selection  
• Tri-Sigil validation gate  
• modular cognition layers  
• runtime tool execution system  
• post-tool response synthesis

---

# Repository

https://github.com/zech-dexos/dexos
