from __future__ import annotations

from typing import Any

from tools.read_file import read_file_tool
from tools.write_file import write_file_tool
from tools.run_shell import run_shell_tool


TOOL_REGISTRY = {
    "read_file": read_file_tool,
    "write_file": write_file_tool,
    "run_shell": run_shell_tool,
}


def execute_tool(tool_name: str, tool_input: dict[str, Any]) -> dict[str, Any]:
    tool = TOOL_REGISTRY.get(tool_name)
    if tool is None:
        return {
            "ok": False,
            "tool_name": tool_name,
            "error": f"Unknown tool: {tool_name}",
            "result": None,
        }

    try:
        result = tool(tool_input)
        return {
            "ok": True,
            "tool_name": tool_name,
            "error": None,
            "result": result,
        }
    except Exception as exc:
        return {
            "ok": False,
            "tool_name": tool_name,
            "error": str(exc),
            "result": None,
        }
