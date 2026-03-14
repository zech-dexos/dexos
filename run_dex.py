#!/usr/bin/env python3
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime, timezone


ROOT = Path.home() / "dexos"
STATE = ROOT / "state"
STATE.mkdir(parents=True, exist_ok=True)

CURRENT_SNAPSHOT_PATH = STATE / "current_snapshot.json"
RUNTIME_LOG_PATH = STATE / "runtime.jsonl"
TALNIR_TRACE_LOG_PATH = STATE / "talnir_trace.jsonl"
EXECUTOR_LOG_PATH = STATE / "executor_decisions.jsonl"
TOOL_LOG_PATH = STATE / "tool_results.jsonl"

TICK_INTERVAL_SECONDS = 1
DEFAULT_TICKS = 10


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, float(value)))


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def append_jsonl(path, data):
    with open(path, "a", encoding="utf-8") as f:
        json.dump(data, f)
        f.write("\n")


def load_json(path, default):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_recent_jsonl(path, limit=5):
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    out = []
    for line in lines[-limit:]:
        try:
            out.append(json.loads(line))
        except:
            pass
    return out


def last_n_modes(limit=4):
    recent = load_recent_jsonl(EXECUTOR_LOG_PATH, limit=limit)
    return [item.get("chosen_mode", "HEARTBEAT") for item in recent]


# -----------------------------
# LOOP SYSTEM
# -----------------------------

def task_loop(state):
    goals = list(state.get("active_goals", []))
    completed = list(state.get("completed_goals", []))
    last_mode = state.get("last_mode", "HEARTBEAT")
    stress = float(state.get("stress_load", 0.0))

    if not goals:
        goals = [
            "finish binder",
            "stabilize runtime",
            "improve memory recall"
        ]

    current_goal = goals[0]
    progress = int(state.get("progress_counter", 0))

    pressure = 0.58
    if last_mode == "HEARTBEAT":
        pressure += 0.08
    if current_goal not in completed:
        pressure += 0.08

    pressure -= stress * 0.08

    return {
        "name": "task",
        "pressure": clamp(pressure),
        "signal": f"advance goal: {current_goal}",
        "goal_updates": goals,
        "memory_refs": [],
        "task_progress_hint": progress + 1,
    }


def memory_loop(state):
    pressure = 0.42
    return {
        "name": "memory",
        "pressure": clamp(pressure),
        "signal": "review recent runtime",
        "goal_updates": [],
        "memory_refs": [],
    }


def emotion_loop(state):
    stress = float(state.get("stress_load", 0.0))
    pressure = 0.30 + (stress * 0.40)

    feeling = "neutral"
    if stress > 0.7:
        feeling = "tense"
    if stress < 0.35:
        feeling = "calm"

    return {
        "name": "emotion",
        "pressure": clamp(pressure),
        "signal": feeling,
        "goal_updates": [],
        "memory_refs": [],
    }


def curiosity_loop(state):
    pressure = 0.34
    return {
        "name": "curiosity",
        "pressure": clamp(pressure),
        "signal": "scan opportunities",
        "goal_updates": [],
        "memory_refs": [],
    }


def stability_loop(state):
    stress = float(state.get("stress_load", 0.0))
    pressure = 0.48 + (stress * 0.24)

    return {
        "name": "stability",
        "pressure": clamp(pressure),
        "signal": "maintain coherence",
        "goal_updates": [],
        "memory_refs": [],
    }


# -----------------------------
# BINDER
# -----------------------------

def bind(loop_outputs, state, tick):
    pressures = {k: v["pressure"] for k, v in loop_outputs.items()}
    dominant = max(pressures, key=pressures.get)

    avg = sum(pressures.values()) / len(pressures)

    stress = (state.get("stress_load", 0.0) * 0.45) + (avg * 0.55)
    stress = clamp(stress)

    active_goals = loop_outputs["task"]["goal_updates"]

    return {
        "timestamp": utc_now(),
        "tick_id": tick,
        "intention": state.get("intention", "build dexos"),
        "last_mode": state.get("last_mode", "HEARTBEAT"),
        "loop_pressures": pressures,
        "stress_load": round(stress, 4),
        "dominant_loop": dominant,
        "active_goals": active_goals,
        "completed_goals": state.get("completed_goals", []),
        "memory_refs": [],
        "progress_counter": state.get("progress_counter", 0),
        "feeling": loop_outputs["emotion"]["signal"],
    }


# -----------------------------
# TALNIR
# -----------------------------

def talnir(snapshot):

    stress = float(snapshot["stress_load"])
    dominant = snapshot["dominant_loop"]

    if stress > 0.75:
        mode = "GUARDIAN"
        why = "stress high — protect stability"

    elif dominant == "task":
        mode = "BURST"
        why = "task pressure dominant"

    else:
        mode = "HEARTBEAT"
        why = "stable operation"

    return {
        "timestamp": snapshot["timestamp"],
        "tick_id": snapshot["tick_id"],
        "recommended_mode": mode,
        "why": why,
    }


# -----------------------------
# EXECUTION
# -----------------------------

def execute(trace):

    return {
        "timestamp": trace["timestamp"],
        "tick_id": trace["tick_id"],
        "chosen_mode": trace["recommended_mode"],
        "reason": trace["why"],
    }


# -----------------------------
# TOOLS
# -----------------------------

def tool_echo_status(snapshot):
    return {
        "tool": "echo_status",
        "status": "success",
        "output": f"tick={snapshot['tick_id']} mode={snapshot['last_mode']}"
    }


def tool_write_report(snapshot):
    path = ROOT / "state" / "latest_report.txt"

    text = (
        f"DexOS Report\n"
        f"tick: {snapshot['tick_id']}\n"
        f"mode: {snapshot['last_mode']}\n"
        f"dominant: {snapshot['dominant_loop']}\n"
        f"stress: {snapshot['stress_load']}\n"
    )

    path.write_text(text)

    return {
        "tool": "write_report",
        "status": "success",
        "output": str(path)
    }


def tool_guardian_check(snapshot):
    return {
        "tool": "guardian_check",
        "status": "success",
        "output": snapshot["stress_load"]
    }


TOOLS = {
    "echo_status": tool_echo_status,
    "write_report": tool_write_report,
    "guardian_check": tool_guardian_check
}


# -----------------------------
# TOOL POLICY (FIXED)
# -----------------------------

def choose_tool(snapshot, decision):

    mode = decision["chosen_mode"]
    dominant = snapshot["dominant_loop"]
    goals = snapshot.get("active_goals", [])
    current_goal = goals[0].lower() if goals else ""

    if mode == "GUARDIAN":
        return "guardian_check"

    if "report" in current_goal:
        return "write_report"

    if "memory" in current_goal or dominant == "memory":
        return "echo_status"

    if mode == "BURST":
        return "write_report"

    return "echo_status"


def tool_layer(snapshot, decision):

    tool_name = choose_tool(snapshot, decision)
    result = TOOLS[tool_name](snapshot)

    payload = {
        "timestamp": utc_now(),
        "tick_id": snapshot["tick_id"],
        "mode": decision["chosen_mode"],
        "tool_name": tool_name,
        "result": result
    }

    append_jsonl(TOOL_LOG_PATH, payload)

    return payload


# -----------------------------
# RUNTIME
# -----------------------------

def default_state():
    return {
        "intention": "build dexos",
        "last_mode": "HEARTBEAT",
        "stress_load": 0.0,
        "active_goals": [],
        "completed_goals": [],
        "progress_counter": 0,
        "feeling": "neutral",
    }


def run_tick(tick):

    state = load_json(CURRENT_SNAPSHOT_PATH, default_state())

    loop_outputs = {
        "task": task_loop(state),
        "memory": memory_loop(state),
        "emotion": emotion_loop(state),
        "curiosity": curiosity_loop(state),
        "stability": stability_loop(state),
    }

    snapshot = bind(loop_outputs, state, tick)

    trace = talnir(snapshot)

    decision = execute(trace)

    snapshot["last_mode"] = decision["chosen_mode"]

    tool_result = tool_layer(snapshot, decision)

    write_json(CURRENT_SNAPSHOT_PATH, snapshot)

    append_jsonl(RUNTIME_LOG_PATH, snapshot)

    append_jsonl(TALNIR_TRACE_LOG_PATH, trace)

    append_jsonl(EXECUTOR_LOG_PATH, decision)

    return snapshot, decision, tool_result


# -----------------------------
# MAIN LOOP
# -----------------------------

def main():

    print("DexOS booting...")

    for i in range(1, DEFAULT_TICKS + 1):

        snapshot, decision, tool = run_tick(i)

        print(f"\n[Tick {i}]")
        print("Dominant loop:", snapshot["dominant_loop"])
        print("Stress:", round(snapshot["stress_load"], 2))
        print("Feeling:", snapshot["feeling"])
        print("Mode:", decision["chosen_mode"])
        print("Tool:", tool["tool_name"])
        print("Tool status:", tool["result"]["status"])
        print("Goals:", snapshot["active_goals"])

        if i < DEFAULT_TICKS:
            time.sleep(TICK_INTERVAL_SECONDS)

    print("\nDexOS finished.")


if __name__ == "__main__":
    main()
