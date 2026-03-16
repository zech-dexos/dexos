from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RUNTIME_DIR = Path(__file__).resolve().parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

from cognition.pipeline import run_cognition_pipeline
from cognition.expression import run_expression
from tools.registry import execute_tool


DATA_DIR = Path(os.environ.get("DEX_DATA_DIR", "./dex_data"))
STATE_FILE = DATA_DIR / "state.json"
MEMORY_FILE = DATA_DIR / "memory.jsonl"
EVENTS_FILE = DATA_DIR / "events.jsonl"
CONSTITUTION_FILE = RUNTIME_DIR.parent / "constitution" / "dex_cognition_v1.txt"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_recent_jsonl(path: Path, limit: int = 25) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        lines = f.readlines()[-limit:]
    out: list[dict[str, Any]] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


@dataclass
class Event:
    event_id: str
    event_type: str
    content: str
    timestamp: str
    source: str = "user"
    committed: bool = False


@dataclass
class DexState:
    identity: str
    mode: str
    feeling: str
    stress: float
    goals: list[str]
    last_continuation: str
    last_response: str
    last_cycle_at: str
    continuity_status: str
    pending_event_count: int


DEFAULT_STATE = DexState(
    identity="Dex",
    mode="HEARTBEAT",
    feeling="steady",
    stress=0.15,
    goals=["maintain continuity", "reflect truthfully", "learn from interaction"],
    last_continuation="maintain_presence",
    last_response="",
    last_cycle_at=utc_now_iso(),
    continuity_status="stable",
    pending_event_count=0,
)


def load_state() -> DexState:
    ensure_data_dir()
    if not STATE_FILE.exists():
        save_state(DEFAULT_STATE)
        return DEFAULT_STATE
    with STATE_FILE.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    return DexState(**raw)


def save_state(state: DexState) -> None:
    ensure_data_dir()
    with STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump(asdict(state), f, indent=2, ensure_ascii=False)


def enqueue_user_message(content: str) -> Event:
    event = Event(
        event_id=f"evt_{int(time.time() * 1000)}",
        event_type="user_message",
        content=content,
        timestamp=utc_now_iso(),
    )
    append_jsonl(EVENTS_FILE, asdict(event))
    return event


def fetch_uncommitted_events() -> list[Event]:
    if not EVENTS_FILE.exists():
        return []

    events: list[Event] = []
    with EVENTS_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                continue
            event = Event(**raw)
            if not event.committed:
                events.append(event)
    return events


def mark_events_committed(event_ids: set[str]) -> None:
    if not EVENTS_FILE.exists() or not event_ids:
        return

    updated: list[dict[str, Any]] = []
    with EVENTS_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            raw = json.loads(line)
            if raw.get("event_id") in event_ids:
                raw["committed"] = True
            updated.append(raw)

    with EVENTS_FILE.open("w", encoding="utf-8") as f:
        for record in updated:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def talnir_reflect(
    state: DexState,
    incoming_events: list[Event],
    recent_memory: list[dict[str, Any]],
) -> dict[str, Any]:
    latest_message = incoming_events[-1].content if incoming_events else ""

    possible_continuations = [
        "maintain_presence",
        "answer_directly",
        "shift_to_engaged",
        "surface_conflict",
        "defer_with_note",
        "use_tool",
    ]

    if latest_message:
        lowered = latest_message.lower()
        if any(word in lowered for word in ["help", "build", "show", "make"]):
            possible_continuations.insert(0, "assist_concretely")
        if any(word in lowered for word in ["how are you", "hello", "hey"]):
            possible_continuations.insert(0, "relational_response")

    memory_summary = []
    for item in recent_memory[-5:]:
        memory_summary.append(
            {
                "timestamp": item.get("timestamp"),
                "continuation": item.get("continuation"),
                "response": item.get("cognition", {}).get("response", ""),
                "event_count": len(item.get("incoming_events", [])),
            }
        )

    return {
        "mirror_time": utc_now_iso(),
        "state_before": asdict(state),
        "incoming_events": [asdict(e) for e in incoming_events],
        "recent_memory_summary": memory_summary,
        "talnir_observations": {
            "continuity_status": state.continuity_status,
            "current_mode": state.mode,
            "stress": state.stress,
            "event_count": len(incoming_events),
            "latest_message": latest_message,
        },
        "possible_continuations": possible_continuations,
    }


def choose_continuation(
    state: DexState,
    talnir_view: dict[str, Any],
    cognition: dict[str, Any],
) -> str:
    latest_message = talnir_view["talnir_observations"].get("latest_message", "")
    available = talnir_view["possible_continuations"]
    suggested = cognition.get("suggested_continuation", "maintain_presence")

    if not latest_message:
        return "maintain_presence"

    if suggested in available:
        return suggested

    return "answer_directly"


def realign_talnir(talnir_view: dict[str, Any], continuation: str) -> dict[str, Any]:
    aligned = dict(talnir_view)
    aligned["realigned_to"] = continuation
    aligned["realignment_time"] = utc_now_iso()
    return aligned


def maybe_execute_tool(cognition: dict[str, Any], continuation: str) -> dict[str, Any] | None:
    if continuation != "use_tool":
        return None

    tool_action = cognition.get("tool_action")
    if not tool_action:
        return None

    tool_name = tool_action.get("tool_name")
    tool_input = tool_action.get("tool_input", {})
    result = execute_tool(tool_name, tool_input)

    cognition["tool_result"] = result
    return result


def apply_continuation(
    state: DexState,
    continuation: str,
    cognition: dict[str, Any],
    incoming_events: list[Event],
) -> DexState:
    next_state = DexState(**asdict(state))
    next_state.last_continuation = continuation
    next_state.last_cycle_at = utc_now_iso()
    next_state.pending_event_count = 0

    if continuation in {"assist_concretely", "answer_directly", "relational_response", "use_tool"}:
        next_state.mode = "ENGAGED"
    elif continuation == "maintain_presence":
        next_state.mode = "HEARTBEAT"

    if incoming_events or continuation == "use_tool":
        next_state.last_response = cognition.get("response", "")

    return next_state


def commit_cycle(
    state_before: DexState,
    state_after: DexState,
    incoming_events: list[Event],
    talnir_view: dict[str, Any],
    cognition: dict[str, Any],
    continuation: str,
) -> None:
    append_jsonl(
        MEMORY_FILE,
        {
            "timestamp": utc_now_iso(),
            "state_before": asdict(state_before),
            "incoming_events": [asdict(e) for e in incoming_events],
            "talnir": talnir_view,
            "cognition": cognition,
            "continuation": continuation,
            "state_after": asdict(state_after),
        },
    )


class DexRuntime:
    def __init__(self, cycle_seconds: float = 2.0) -> None:
        self.cycle_seconds = cycle_seconds

    def run_forever(self) -> None:
        print("Dex entity online. Loop forming before any user message.")
        while True:
            self.run_one_cycle()
            time.sleep(self.cycle_seconds)

    def run_one_cycle(self) -> None:
        state_before = load_state()
        incoming_events = fetch_uncommitted_events()
        recent_memory = read_recent_jsonl(MEMORY_FILE, limit=10)

        state_before.pending_event_count = len(incoming_events)

        talnir_view = talnir_reflect(state_before, incoming_events, recent_memory)
        cognition = run_cognition_pipeline(
            state=asdict(state_before),
            talnir_view=talnir_view,
            recent_memory=recent_memory,
            constitution_path=CONSTITUTION_FILE,
        )
        continuation = choose_continuation(state_before, talnir_view, cognition)
        tool_result = maybe_execute_tool(cognition, continuation)

        if continuation == "use_tool" and tool_result is not None:
            expression = run_expression(
                talnir_view["talnir_observations"].get("latest_message", ""),
                cognition["layers"]["tri_sigil"],
                cognition["layers"]["talnir"],
                tool_result=tool_result,
            )
            cognition["layers"]["expression"] = expression
            cognition["response"] = expression.get("final_response", "")
            cognition["candidate_responses"] = [cognition["response"]] if cognition["response"] else []
            cognition["tool_result"] = tool_result

        aligned_talnir = realign_talnir(talnir_view, continuation)
        state_after = apply_continuation(state_before, continuation, cognition, incoming_events)

        save_state(state_after)

        should_commit = (
            bool(incoming_events)
            or continuation != state_before.last_continuation
            or continuation == "use_tool"
        )
        if should_commit:
            commit_cycle(
                state_before=state_before,
                state_after=state_after,
                incoming_events=incoming_events,
                talnir_view=aligned_talnir,
                cognition=cognition,
                continuation=continuation,
            )

        mark_events_committed({e.event_id for e in incoming_events})

        response = cognition.get("response", "")
        if response:
            print(f"Dex: {response}")

        if tool_result:
            print(f"Tool result: {json.dumps(tool_result, ensure_ascii=False)}")

    def run_talk_cli(self) -> None:
        print("Type messages to Dex. They will enter the living loop.")
        print("Type 'exit' to leave the input shell.")
        while True:
            user = input("You: ").strip()
            if not user:
                continue
            if user.lower() in {"exit", "quit"}:
                break
            event = enqueue_user_message(user)
            print(f"Queued for Dex loop: {event.event_id}")


def run_talk_cli() -> None:
    DexRuntime().run_talk_cli()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="DexOS unified entity loop scaffold")
    parser.add_argument("mode", choices=["run", "talk", "cycle"])
    parser.add_argument("--seconds", type=float, default=2.0)
    args = parser.parse_args()

    ensure_data_dir()

    if args.mode == "run":
        DexRuntime(cycle_seconds=args.seconds).run_forever()
    elif args.mode == "talk":
        run_talk_cli()
    elif args.mode == "cycle":
        DexRuntime(cycle_seconds=args.seconds).run_one_cycle()
        print("Ran one Dex cycle.")
