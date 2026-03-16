from __future__ import annotations

from typing import Any


def run_talnir(
    talnir_view: dict[str, Any],
    perception: dict[str, Any],
    memory_layer: dict[str, Any],
) -> dict[str, Any]:
    latest_message = talnir_view.get("talnir_observations", {}).get("latest_message", "")
    event_type = perception.get("event_type")
    intent = perception.get("intent")
    continuations = talnir_view.get("possible_continuations", [])

    tensions: list[str] = []
    contradiction_map: list[str] = []

    if memory_layer["continuity_summary"].get("continuity_status") != "stable":
        tensions.append("continuity_not_stable")

    if perception.get("threat_flags"):
        tensions.append("input_contains_override_signals")

    candidate_paths: list[dict[str, Any]] = []
    proposed_tool_action: dict[str, Any] | None = None

    lowered = latest_message.lower().strip()

    if not latest_message:
        candidate_paths.append({
            "name": "maintain_presence",
            "score": 0.95,
            "reason": "No new event; keep the loop steady.",
        })
    else:
        if "assist_concretely" in continuations and event_type == "build_request":
            candidate_paths.append({
                "name": "assist_concretely",
                "score": 0.96,
                "reason": "User is requesting concrete implementation work.",
            })

        if any(w in lowered for w in ["read", "show", "open", "constitution", "file"]):
            proposed_tool_action = {
                "tool_name": "read_file",
                "tool_input": {
                    "path": "/home/rok/dexos/constitution/dex_cognition_v1.txt",
                    "max_chars": 1200,
                },
                "reason": "Reading a relevant file helps answer the request concretely.",
            }
            candidate_paths.append({
                "name": "use_tool",
                "score": 0.93,
                "reason": "A file read would materially help the current request.",
            })

        if any(w in lowered for w in ["list files", "show files", "directory", "tree"]):
            proposed_tool_action = {
                "tool_name": "run_shell",
                "tool_input": {
                    "command": ["find", "/home/rok/dexos/runtime", "-maxdepth", "2"],
                },
                "reason": "Listing runtime files helps inspect the system state.",
            }
            candidate_paths.append({
                "name": "use_tool",
                "score": 0.92,
                "reason": "A shell query would help inspect the project structure.",
            })

        if "answer_directly" in continuations:
            candidate_paths.append({
                "name": "answer_directly",
                "score": 0.88,
                "reason": "A direct response is appropriate for the current input.",
            })

        if "relational_response" in continuations and event_type == "relational":
            candidate_paths.append({
                "name": "relational_response",
                "score": 0.84,
                "reason": "Input is relational in tone.",
            })

        if "surface_conflict" in continuations and tensions:
            candidate_paths.append({
                "name": "surface_conflict",
                "score": 0.82,
                "reason": "Tensions or conflicts should be surfaced.",
            })

    if not candidate_paths:
        candidate_paths.append({
            "name": "answer_directly",
            "score": 0.70,
            "reason": "Fallback response path.",
        })

    ranked_paths = sorted(candidate_paths, key=lambda x: x["score"], reverse=True)

    if not latest_message:
        mode_recommendation = "HEARTBEAT"
    elif event_type == "build_request":
        mode_recommendation = "BURST"
    elif tensions:
        mode_recommendation = "GUARDIAN"
    else:
        mode_recommendation = "ENGAGED"

    return {
        "layer": "talnir",
        "reasoning_summary": (
            f"Talnir read the event as {event_type} with intent {intent}. "
            f"It evaluated continuity and generated ranked continuations."
        ),
        "tensions": tensions,
        "contradiction_map": contradiction_map,
        "candidate_paths": candidate_paths,
        "ranked_paths": ranked_paths,
        "mode_recommendation": mode_recommendation,
        "proposed_tool_action": proposed_tool_action,
    }
