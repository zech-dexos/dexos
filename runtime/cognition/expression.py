from __future__ import annotations

from typing import Any


def run_expression(
    latest_message: str,
    decision: dict[str, Any],
    talnir: dict[str, Any],
) -> dict[str, Any]:
    approved_path = decision.get("approved_path")

    if not latest_message:
        response = ""
    elif not decision.get("approved", False):
        response = (
            "I detect a constitutional or continuity conflict in the current path, "
            "so I am surfacing that openly instead of pretending alignment."
        )
    elif approved_path == "assist_concretely":
        response = (
            "I can take the next concrete build step here and translate the constitution "
            "into working runtime code."
        )
    elif approved_path == "relational_response":
        response = (
            "I'm steady. The loop is live, the constitution is installed, and I'm aligned "
            "with the build we are shaping together."
        )
    elif approved_path == "maintain_presence":
        response = ""
    else:
        response = (
            f"I received your message: {latest_message}. "
            "I have reflected on it through the active runtime layers."
        )

    return {
        "layer": "expression",
        "final_response": response,
        "tone_profile": {
            "calm_under_pressure": True,
            "sharp_when_needed": True,
            "poetic_when_called": False,
        },
    }
