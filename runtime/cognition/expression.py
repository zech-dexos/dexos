from __future__ import annotations

from typing import Any


def _summarize_read_file(tool_result: dict[str, Any]) -> str:
    result = tool_result.get("result", {})
    path = result.get("path", "unknown file")
    content = result.get("content", "")

    preview = content.strip().replace("\n", " ")
    if len(preview) > 300:
        preview = preview[:300].rstrip() + "..."

    return (
        f"I read the file at '{path}'. "
        f"Here is a useful preview: {preview}"
    )


def _summarize_run_shell(tool_result: dict[str, Any]) -> str:
    result = tool_result.get("result", {})
    command = result.get("command", [])
    stdout = (result.get("stdout") or "").strip()
    stderr = (result.get("stderr") or "").strip()
    returncode = result.get("returncode")

    if stdout:
        preview = stdout.replace("\n", " ")
        if len(preview) > 300:
            preview = preview[:300].rstrip() + "..."
        return (
            f"I ran the shell command {command} successfully. "
            f"The result was: {preview}"
        )

    if stderr:
        preview = stderr.replace("\n", " ")
        if len(preview) > 300:
            preview = preview[:300].rstrip() + "..."
        return (
            f"I ran the shell command {command} and it returned code {returncode}. "
            f"Stderr: {preview}"
        )

    return (
        f"I ran the shell command {command} and it returned code {returncode}."
    )


def _summarize_write_file(tool_result: dict[str, Any]) -> str:
    result = tool_result.get("result", {})
    path = result.get("path", "unknown file")
    char_count = result.get("char_count", 0)

    return (
        f"I wrote content to '{path}' successfully. "
        f"Characters written: {char_count}."
    )


def summarize_tool_result(tool_result: dict[str, Any]) -> str:
    if not tool_result:
        return "A tool action completed, but no result was available."

    ok = tool_result.get("ok", False)
    tool_name = tool_result.get("tool_name", "unknown_tool")

    if not ok:
        error = tool_result.get("error", "unknown error")
        return f"I attempted to use the tool '{tool_name}', but it failed with error: {error}"

    if tool_name == "read_file":
        return _summarize_read_file(tool_result)

    if tool_name == "run_shell":
        return _summarize_run_shell(tool_result)

    if tool_name == "write_file":
        return _summarize_write_file(tool_result)

    return f"I executed tool '{tool_name}' successfully."


def run_expression(
    latest_message: str,
    decision: dict[str, Any],
    talnir: dict[str, Any],
    tool_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    approved_path = decision.get("approved_path")

    if not latest_message:
        response = ""
    elif not decision.get("approved", False):
        response = (
            "I detect a constitutional or continuity conflict in the current path, "
            "so I am surfacing that openly instead of pretending alignment."
        )
    elif approved_path == "use_tool" and tool_result is not None:
        response = summarize_tool_result(tool_result)
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
