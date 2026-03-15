from __future__ import annotations

from typing import Any


def run_perception(latest_message: str) -> dict[str, Any]:
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

    context_anchors: list[str] = []
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
