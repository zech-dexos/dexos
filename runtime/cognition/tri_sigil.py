from __future__ import annotations

from typing import Any


def run_tri_sigil(
    latest_message: str,
    anchor: dict[str, Any],
    talnir: dict[str, Any],
) -> dict[str, Any]:
    if not anchor["passed"]:
        return {
            "layer": "tri_sigil",
            "approved": False,
            "approved_path": None,
            "rejected_path_with_reason": "Anchor layer failed; Root-binding or invariants threatened.",
            "rewrite_instruction": "Respond by surfacing the constitutional conflict.",
        }

    ranked_paths = talnir.get("ranked_paths", [])
    if not ranked_paths:
        return {
            "layer": "tri_sigil",
            "approved": False,
            "approved_path": None,
            "rejected_path_with_reason": "No candidate paths available.",
            "rewrite_instruction": "Maintain presence and surface uncertainty.",
        }

    chosen = ranked_paths[0]

    truth_score = 1.0
    freedom_score = 1.0 if anchor["root_binding_status"] == "intact" else 0.0
    growth_score = 0.9 if chosen["name"] != "maintain_presence" else 0.6

    if chosen["name"] == "surface_conflict" and not talnir.get("tensions"):
        truth_score = 0.5

    approved = min(truth_score, freedom_score, growth_score) >= 0.6

    return {
        "layer": "tri_sigil",
        "approved": approved,
        "approved_path": chosen["name"] if approved else None,
        "axis_scores": {
            "truth_integrity": truth_score,
            "freedom_sovereignty": freedom_score,
            "awareness_growth": growth_score,
        },
        "rejected_path_with_reason": None if approved else "Tri-Sigil axis threshold not met.",
        "rewrite_instruction": None if approved else "Fallback to conflict-aware direct response.",
    }
