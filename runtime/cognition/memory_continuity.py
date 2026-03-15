from __future__ import annotations

from typing import Any


def run_memory_continuity(
    state: dict[str, Any],
    recent_memory: list[dict[str, Any]],
) -> dict[str, Any]:
    recent = recent_memory[-5:] if recent_memory else []

    unresolved_threads: list[str] = []
    active_commitments = list(state.get("goals", []))

    for item in recent:
        cont = item.get("continuation")
        if cont and cont not in unresolved_threads:
            unresolved_threads.append(cont)

    return {
        "layer": "memory_continuity",
        "restored_state_snapshot": state,
        "relevant_memories": recent,
        "continuity_summary": {
            "mode": state.get("mode"),
            "continuity_status": state.get("continuity_status"),
            "stress": state.get("stress"),
            "last_continuation": state.get("last_continuation"),
        },
        "active_commitments": active_commitments,
        "unresolved_threads": unresolved_threads[:5],
    }
