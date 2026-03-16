from __future__ import annotations

from pathlib import Path
from typing import Any


def read_file_tool(tool_input: dict[str, Any]) -> dict[str, Any]:
    path_str = tool_input.get("path")
    if not path_str:
        raise ValueError("read_file requires 'path'")

    path = Path(path_str).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    content = path.read_text(encoding="utf-8")
    max_chars = int(tool_input.get("max_chars", 4000))

    return {
        "path": str(path),
        "content": content[:max_chars],
        "truncated": len(content) > max_chars,
        "char_count": len(content),
    }
