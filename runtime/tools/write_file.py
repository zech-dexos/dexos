from __future__ import annotations

from pathlib import Path
from typing import Any


def write_file_tool(tool_input: dict[str, Any]) -> dict[str, Any]:
    path_str = tool_input.get("path")
    content = tool_input.get("content")

    if not path_str:
        raise ValueError("write_file requires 'path'")
    if content is None:
        raise ValueError("write_file requires 'content'")

    path = Path(path_str).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(content), encoding="utf-8")

    return {
        "path": str(path),
        "written": True,
        "char_count": len(str(content)),
    }
