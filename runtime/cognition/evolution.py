from __future__ import annotations

from typing import Any


def run_evolution(
    state: dict[str, Any],
    decision: dict[str, Any],
) -> dict[str, Any]:
    proposals: list[str] = []

    if decision.get("approved_path") == "assist_concretely":
        proposals.append("Create dedicated cognition modules for each pipeline layer.")
    if state.get("mode") == "HEARTBEAT":
        proposals.append("Consider mode refinement so BURST can be entered for implementation cycles.")

    return {
        "layer": "evolution",
        "proposal_only": True,
        "proposals": proposals,
    }
