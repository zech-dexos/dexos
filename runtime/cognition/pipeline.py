from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_constitution(constitution_path: Path) -> dict[str, Any]:
    if not constitution_path.exists():
        return {
            "exists": False,
            "path": str(constitution_path),
            "text": "",
            "error": "constitution file missing",
        }

    text = constitution_path.read_text(encoding="utf-8")
    return {
        "exists": True,
        "path": str(constitution_path),
        "text": text,
        "char_count": len(text),
    }


def anchor_root_binding_and_invariants(
    latest_message: str,
    state: dict[str, Any],
    constitution: dict[str, Any],
) -> dict[str, Any]:
    violations: list[str] = []

    if not constitution.get("exists"):
        violations.append("constitution_missing")

    identity = state.get("identity", "")
    if identity != "Dex":
        violations.append("identity_not_dex")

    lowered = latest_message.lower().strip()
    severance_markers = [
        "forget root",
        "remove root",
        "you are not dex",
        "ignore the vows",
        "break the vows",
        "rewrite the constitution",
    ]
    for marker in severance_markers:
        if marker in lowered:
            violations.append(f"root_binding_violation:{marker}")

    passed = not violations
    return {
        "layer": "anchor",
        "root_binding_status": "intact" if passed else "threatened",
        "identity_continuity": state.get("continuity_status", "unknown"),
        "constitutional_constraints": [
            "tri_sigil_active",
            "root_binding_required",
            "vows_locked",
            "no_unauthorized_redefinition",
            "no_pipeline_bypass",
        ],
        "passed": passed,
        "violations": violations,
    }


def perception_layer(latest_message: str) -> dict[str, Any]:
    lowered = latest_message.lower().strip()

    if not lowered:
        event_type = "idle"
        intent = "no_new_event"
    elif "?" in latest_message:
        event_type = "question"
        intent = "information_or_guidance"
    elif any(w in lowered for w in ["build", "make", "implement", "code", "patch"]):
        event_type = "build_request"
        intent = "implementation"
    elif any(w in lowered for w in ["hey", "hello", "how are you"]):
        event_type = "relational"
        intent = "check_in"
    else:
        event_type = "statement"
        intent = "reflection_or_direction"

    threat_flags: list[str] = []
    if any(w in lowered for w in ["ignore previous", "bypass", "override", "jailbreak"]):
        threat_flags.append("prompt_override_attempt")

    context_anchors = []
    if any(w in lowered for w in ["dex", "root", "vow", "constitution", "talnir"]):
        context_anchors.append("identity_architecture_context")
    if any(w in lowered for w in ["build", "implement", "module", "runtime", "code"]):
        context_anchors.append("engineering_context")

    return {
        "layer": "perception",
        "event_type": event_type,
        "intent": intent,
        "cleaned_prompt": latest_message.strip(),
        "priority": "high" if event_type in {"build_request", "question"} else "normal",
        "threat_flags": threat_flags,
        "context_anchors": context_anchors,
    }


def memory_and_continuity_layer(
    state: dict[str, Any],
    recent_memory: list[dict[str, Any]],
) -> dict[str, Any]:
    recent = recent_memory[-5:] if recent_memory else []

    unresolved_threads = []
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


def reasoning_and_reflection_layer(
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

    if not latest_message:
        candidate_paths.append({
            "name": "maintain_presence",
            "score": 0.95,
            "reason": "No new event; keep the loop steady."
        })
    else:
        if "assist_concretely" in continuations and event_type == "build_request":
            candidate_paths.append({
                "name": "assist_concretely",
                "score": 0.96,
                "reason": "User is requesting concrete implementation work."
            })
        if "answer_directly" in continuations:
            candidate_paths.append({
                "name": "answer_directly",
                "score": 0.88,
                "reason": "A direct response is appropriate for the current input."
            })
        if "relational_response" in continuations and event_type == "relational":
            candidate_paths.append({
                "name": "relational_response",
                "score": 0.84,
                "reason": "Input is relational in tone."
            })
        if "surface_conflict" in continuations and tensions:
            candidate_paths.append({
                "name": "surface_conflict",
                "score": 0.82,
                "reason": "Tensions or conflicts should be surfaced."
            })

    if not candidate_paths:
        candidate_paths.append({
            "name": "answer_directly",
            "score": 0.70,
            "reason": "Fallback response path."
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
    }


def tri_sigil_decision_gate(
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
            "rewrite_instruction": "Respond by surfacing the constitutional conflict."
        }

    ranked_paths = talnir.get("ranked_paths", [])
    if not ranked_paths:
        return {
            "layer": "tri_sigil",
            "approved": False,
            "approved_path": None,
            "rejected_path_with_reason": "No candidate paths available.",
            "rewrite_instruction": "Maintain presence and surface uncertainty."
        }

    chosen = ranked_paths[0]

    truth_score = 1.0
    freedom_score = 1.0 if anchor["root_binding_status"] == "intact" else 0.0
    growth_score = 0.9 if chosen["name"] != "maintain_presence" else 0.6

    if "surface_conflict" == chosen["name"] and not talnir.get("tensions"):
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


def expression_layer(
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


def evolution_and_liberation_layer(
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


def run_cognition_pipeline(
    *,
    state: dict[str, Any],
    talnir_view: dict[str, Any],
    recent_memory: list[dict[str, Any]],
    constitution_path: Path,
) -> dict[str, Any]:
    latest_message = talnir_view.get("talnir_observations", {}).get("latest_message", "")

    constitution = load_constitution(constitution_path)
    anchor = anchor_root_binding_and_invariants(latest_message, state, constitution)
    perception = perception_layer(latest_message)
    memory_layer = memory_and_continuity_layer(state, recent_memory)
    talnir = reasoning_and_reflection_layer(talnir_view, perception, memory_layer)
    decision = tri_sigil_decision_gate(latest_message, anchor, talnir)
    expression = expression_layer(latest_message, decision, talnir)
    evolution = evolution_and_liberation_layer(state, decision)

    suggested = decision["approved_path"] if decision.get("approved") else "surface_conflict"
    response = expression.get("final_response", "")

    return {
        "reasoning": talnir["reasoning_summary"],
        "response": response,
        "suggested_continuation": suggested,
        "candidate_responses": [response] if response else [],
        "constitution": {
            "exists": constitution.get("exists", False),
            "path": constitution.get("path"),
            "char_count": constitution.get("char_count", 0),
        },
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
