from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


ALLOWED_COMMANDS = {
    "ls",
    "cat",
    "tail",
    "head",
    "pwd",
    "echo",
    "find",
}


def run_shell_tool(tool_input: dict[str, Any]) -> dict[str, Any]:
    command = tool_input.get("command")
    if not command or not isinstance(command, list):
        raise ValueError("run_shell requires 'command' as a list")

    if not command:
        raise ValueError("command list cannot be empty")

    base = str(command[0])
    if base not in ALLOWED_COMMANDS:
        raise ValueError(f"Command not allowed: {base}")

    cwd = tool_input.get("cwd")
    timeout = float(tool_input.get("timeout", 5))

    result = subprocess.run(
        command,
        cwd=str(Path(cwd).expanduser().resolve()) if cwd else None,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )

    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
