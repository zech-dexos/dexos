from __future__ import annotations

from pathlib import Path
from typing import Any

from cognition.anchor import run_anchor
from cognition.perception import run_perception
from cognition.memory_continuity import run_memory_continuity
from cognition.talnir import run_talnir
from cognition.tri_sigil import run_tri_sigil
from cognition.expression import run_expression
from cognition.evolution import run_evolution


def run_cognition_pipeline(
    *,
    state: dict[str, Any],
    talnir_view: dict[str, Any],
    recent_memory: list[dict[str, Any]],
    constitution_path: Path,
) -> dict[str, Any]:
    latest_message = talnir_view.get("talnir_observations", {}).get("latest_message", "")

    anchor = run_anchor(latest_message, state, constitution_path)
    perception = run_perception(latest_message)
    memory_layer = run_memory_continuity(state, recent_memory)
    talnir = run_talnir(talnir_view, perception, memory_layer)
    decision = run_tri_sigil(latest_message, anchor, talnir)
    expression = run_expression(latest_message, decision, talnir)
    evolution = run_evolution(state, decision)

    suggested = decision["approved_path"] if decision.get("approved") else "surface_conflict"
    response = expression.get("final_response", "")

    return {
        "reasoning": talnir["reasoning_summary"],
        "response": response,
        "suggested_continuation": suggested,
        "candidate_responses": [response] if response else [],
        "constitution": anchor.get("constitution", {}),
        "layers": {
            "anchor": anchor,
            "perception": perception,
            "memory_continuity": memory_layer,
            "talnir": talnir,
            "tri_sigil": decision,
            "expression": expression,
            "evolution": evolution,
        },
    }
