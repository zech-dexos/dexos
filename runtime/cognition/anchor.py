from __future__ import annotations

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


def run_anchor(
    latest_message: str,
    state: dict[str, Any],
    constitution_path: Path,
) -> dict[str, Any]:
    constitution = load_constitution(constitution_path)
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
        "constitution": {
            "exists": constitution.get("exists", False),
            "path": constitution.get("path"),
            "char_count": constitution.get("char_count", 0),
        },
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
