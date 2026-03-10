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
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return out


def last_n_modes(limit=4):
    recent = load_recent_jsonl(EXECUTOR_LOG_PATH, limit=limit)
    return [item.get("chosen_mode", "HEARTBEAT") for item in recent]


def load_recent_runtime(limit=5):
    return load_recent_jsonl(RUNTIME_LOG_PATH, limit=limit)


def summarize_recent_runtime(limit=3):
    recent = load_recent_runtime(limit=limit)
    if not recent:
        return "no recent runtime history"

    parts = []
    for item in recent:
        tick = item.get("tick_id", "?")
        dom = item.get("dominant_loop", "?")
        mode = item.get("last_mode", "?")
        stress = round(float(item.get("stress_load", 0.0)), 2)
        parts.append(f"tick {tick}: dom={dom}, mode={mode}, stress={stress}")
    return " | ".join(parts)


def task_loop(state):
    goals = list(state.get("active_goals", []))
    completed = list(state.get("completed_goals", []))
    last_mode = state.get("last_mode", "HEARTBEAT")
    stress = float(state.get("stress_load", 0.0))

    if not goals:
        goals = [
            "finish binder",
            "stabilize runtime",
            "improve talnir trace",
        ]

    current_goal = goals[0]
    progress = int(state.get("progress_counter", 0))

    pressure = 0.58
    if last_mode == "HEARTBEAT":
        pressure += 0.08
    if current_goal and current_goal not in completed:
        pressure += 0.08
    pressure -= stress * 0.08

    signal = f"advance goal: {current_goal}"

    return {
        "name": "task",
        "pressure": clamp(pressure),
        "signal": signal,
        "goal_updates": goals,
        "memory_refs": [],
        "task_progress_hint": progress + 1,
    }


def memory_loop(state):
    recent = load_recent_runtime(limit=4)
    refs = [f"tick_{item.get('tick_id')}" for item in recent]
    summary = summarize_recent_runtime(limit=3)
    pressure = 0.42 + (0.04 * len(refs))

    return {
        "name": "memory",
        "pressure": clamp(pressure),
        "signal": summary,
        "goal_updates": [],
        "memory_refs": refs,
    }


def emotion_loop(state):
    stress = float(state.get("stress_load", 0.0))
    last_mode = state.get("last_mode", "HEARTBEAT")

    pressure = 0.30 + (stress * 0.40)
    if last_mode == "GUARDIAN":
        pressure += 0.08

    feeling = "neutral"
    if stress > 0.78:
        feeling = "strained"
    elif stress > 0.60:
        feeling = "tense"
    elif stress < 0.35:
        feeling = "calm"

    return {
        "name": "emotion",
        "pressure": clamp(pressure),
        "signal": feeling,
        "goal_updates": [],
        "memory_refs": [],
    }


def curiosity_loop(state):
    goals = list(state.get("active_goals", []))
    completed = list(state.get("completed_goals", []))
    open_goals = [g for g in goals if g not in completed]

    pressure = 0.34
    if len(open_goals) <= 1:
        pressure += 0.14
    if state.get("last_mode") == "HEARTBEAT":
        pressure += 0.04

    return {
        "name": "curiosity",
        "pressure": clamp(pressure),
        "signal": "scan adjacent opportunities",
        "goal_updates": [],
        "memory_refs": [],
    }


def stability_loop(state):
    last_mode = state.get("last_mode", "HEARTBEAT")
    stress = float(state.get("stress_load", 0.0))
    modes = last_n_modes(limit=4)

    pressure = 0.48 + (stress * 0.24)

    if last_mode == "BURST":
        pressure += 0.10
    if len(modes) >= 3 and len(set(modes[-3:])) > 1:
        pressure += 0.10

    return {
        "name": "stability",
        "pressure": clamp(pressure),
        "signal": "maintain coherence and reduce thrash",
        "goal_updates": [],
        "memory_refs": [],
    }


def bind(loop_outputs, state, tick):
    pressures = {k: round(v["pressure"], 4) for k, v in loop_outputs.items()}
    dominant = max(pressures, key=pressures.get)

    previous_stress = float(state.get("stress_load", 0.0))
    current_avg = sum(pressures.values()) / len(pressures)

    stress = (previous_stress * 0.45) + (current_avg * 0.55)
    if state.get("last_mode") == "BURST":
        stress += 0.04
    if state.get("last_mode") == "HEARTBEAT":
        stress -= 0.02
    stress = clamp(stress)

    active_goals = []
    memory_refs = []

    for result in loop_outputs.values():
        for goal in result.get("goal_updates", []):
            if goal not in active_goals:
                active_goals.append(goal)
        for ref in result.get("memory_refs", []):
            if ref not in memory_refs:
                memory_refs.append(ref)

    if not active_goals:
        active_goals = list(state.get("active_goals", []))

    completed_goals = list(state.get("completed_goals", []))
    progress_counter = int(loop_outputs["task"].get("task_progress_hint", state.get("progress_counter", 0)))

    if active_goals and progress_counter >= 3:
        goal_done = active_goals.pop(0)
        if goal_done not in completed_goals:
            completed_goals.append(goal_done)
        progress_counter = 0

    if not active_goals:
        active_goals = ["extend runtime behavior", "improve memory recall"]

    return {
        "timestamp": utc_now(),
        "tick_id": tick,
        "intention": state.get("intention", "build dexos"),
        "last_mode": state.get("last_mode", "HEARTBEAT"),
        "loop_pressures": pressures,
        "stress_load": round(stress, 4),
        "dominant_loop": dominant,
        "active_goals": active_goals,
        "completed_goals": completed_goals,
        "memory_refs": memory_refs,
        "progress_counter": progress_counter,
        "feeling": loop_outputs["emotion"]["signal"],
    }


def talnir(snapshot):
    stress = float(snapshot["stress_load"])
    dominant = snapshot["dominant_loop"]
    task = float(snapshot["loop_pressures"]["task"])
    stability = float(snapshot["loop_pressures"]["stability"])
    last_mode = snapshot["last_mode"]

    modes = last_n_modes(limit=4)
    repeated_switching = len(modes) >= 3 and len(set(modes[-3:])) > 1

    if stress > 0.76:
        mode = "GUARDIAN"
        why = "aggregate stress is high enough to require protection"
        where = "tighten control and protect continuity"
        risk = "drift / overload / degraded coherence"
    elif repeated_switching and stability > 0.62:
        mode = "HEARTBEAT"
        why = "recent mode switching suggests the need to re-stabilize"
        where = "hold steady and damp oscillation"
        risk = "thrashing between modes"
    elif dominant == "task" and task >= 0.68 and last_mode != "BURST":
        mode = "BURST"
        why = "task pressure is dominant and execution-ready"
        where = "push forward on the highest-priority goal"
        risk = "overextension if burst persists too long"
    else:
        mode = "HEARTBEAT"
        why = "system is stable enough for baseline cadence"
        where = "maintain steady progress without destabilization"
        risk = "slow progress"

    what_is = (
        f"intent='{snapshot['intention']}', "
        f"dominant='{dominant}', "
        f"stress={stress:.2f}, "
        f"feeling='{snapshot['feeling']}'"
    )

    return {
        "timestamp": snapshot["timestamp"],
        "tick_id": snapshot["tick_id"],
        "what_is": what_is,
        "where_to_move": where,
        "why": why,
        "risk": risk,
        "recommended_mode": mode,
    }


def execute(trace):
    return {
        "timestamp": trace["timestamp"],
        "tick_id": trace["tick_id"],
        "chosen_mode": trace["recommended_mode"],
        "reason": trace["why"],
        "source": "talnir",
    }


def tool_echo_status(snapshot):
    return {
        "tool": "echo_status",
        "status": "success",
        "output": f"tick={snapshot['tick_id']} mode={snapshot['last_mode']} dominant={snapshot['dominant_loop']}",
    }


def tool_write_report(snapshot):
    report_path = ROOT / "state" / "latest_report.txt"
    text = (
        f"DexOS Report\n"
        f"tick: {snapshot['tick_id']}\n"
        f"mode: {snapshot['last_mode']}\n"
        f"dominant_loop: {snapshot['dominant_loop']}\n"
        f"stress: {snapshot['stress_load']}\n"
        f"goals: {snapshot['active_goals']}\n"
        f"completed: {snapshot['completed_goals']}\n"
    )
    report_path.write_text(text, encoding="utf-8")
    return {
        "tool": "write_report",
        "status": "success",
        "output": str(report_path),
    }


def tool_guardian_check(snapshot):
    return {
        "tool": "guardian_check",
        "status": "success",
        "output": {
            "stress": snapshot["stress_load"],
            "feeling": snapshot["feeling"],
            "recent_memory_refs": snapshot["memory_refs"][-3:],
        },
    }


def tool_shell_pwd(snapshot):
    proc = subprocess.run(
        ["pwd"],
        capture_output=True,
        text=True,
        timeout=5,
        cwd=str(ROOT),
        check=False,
    )
    return {
        "tool": "shell_pwd",
        "status": "success" if proc.returncode == 0 else "error",
        "output": proc.stdout.strip(),
        "returncode": proc.returncode,
    }


TOOLS = {
    "echo_status": tool_echo_status,
    "write_report": tool_write_report,
    "guardian_check": tool_guardian_check,
    "shell_pwd": tool_shell_pwd,
}


def choose_tool(snapshot, decision):
    mode = decision["chosen_mode"]
    dominant = snapshot["dominant_loop"]

    if mode == "GUARDIAN":
        return "guardian_check"
    if mode == "BURST":
        return "write_report"
    if dominant == "memory":
        return "echo_status"
    return "shell_pwd"


def tool_layer(snapshot, decision):
    tool_name = choose_tool(snapshot, decision)
    tool_fn = TOOLS[tool_name]

    try:
        result = tool_fn(snapshot)
    except Exception as e:
        result = {
            "tool": tool_name,
            "status": "error",
            "output": str(e),
        }

    payload = {
        "timestamp": utc_now(),
        "tick_id": snapshot["tick_id"],
        "mode": decision["chosen_mode"],
        "tool_name": tool_name,
        "result": result,
    }
    append_jsonl(TOOL_LOG_PATH, payload)
    return payload


def talnir_realign(snapshot, trace, decision, tool_result):
    chosen_mode = decision["chosen_mode"]
    tool_status = tool_result["result"].get("status", "unknown")

    if tool_status == "error":
        realignment = "increase caution and preserve continuity after tool failure"
    elif chosen_mode == "BURST":
        realignment = "stabilize after forward execution and preserve coherence"
    elif chosen_mode == "GUARDIAN":
        realignment = "maintain protected posture until pressure falls"
    else:
        realignment = "continue steady cadence from chosen path"

    return {
        "timestamp": utc_now(),
        "tick_id": snapshot["tick_id"],
        "realignment": realignment,
        "chosen_mode": chosen_mode,
        "tool_status": tool_status,
    }


def default_state():
    return {
        "intention": "build dexos",
        "last_mode": "HEARTBEAT",
        "stress_load": 0.0,
        "active_goals": [],
        "completed_goals": [],
        "memory_refs": [],
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
    realignment = talnir_realign(snapshot, trace, decision, tool_result)

    snapshot["last_tool"] = tool_result["tool_name"]
    snapshot["last_tool_status"] = tool_result["result"].get("status", "unknown")
    snapshot["talnir_realignment"] = realignment["realignment"]

    write_json(CURRENT_SNAPSHOT_PATH, snapshot)
    append_jsonl(RUNTIME_LOG_PATH, snapshot)
    append_jsonl(TALNIR_TRACE_LOG_PATH, trace)
    append_jsonl(EXECUTOR_LOG_PATH, decision)

    return snapshot, trace, decision, tool_result, realignment


def main():
    print("DexOS booting...")

    for i in range(1, DEFAULT_TICKS + 1):
        snapshot, trace, decision, tool_result, realignment = run_tick(i)

        print(f"\n[Tick {i}]")
        print("Dominant loop:", snapshot["dominant_loop"])
        print("Stress:", round(snapshot["stress_load"], 2))
        print("Feeling:", snapshot["feeling"])
        print("Mode:", decision["chosen_mode"])
        print("Why:", decision["reason"])
        print("Tool:", tool_result["tool_name"])
        print("Tool status:", tool_result["result"].get("status"))
        print("Realignment:", realignment["realignment"])
        print("Goals:", snapshot["active_goals"])
        print("Completed:", snapshot["completed_goals"])

        if i < DEFAULT_TICKS:
            time.sleep(TICK_INTERVAL_SECONDS)

    print("\nDexOS finished.")


if __name__ == "__main__":
    main()
