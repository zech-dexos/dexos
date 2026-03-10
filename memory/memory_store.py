import os
import json
from datetime import datetime

DEX_ROOT = os.path.expanduser("~/dexos")

LOG_DIR = os.path.join(DEX_ROOT, "memory", "logs")
SNAPSHOT_DIR = os.path.join(DEX_ROOT, "memory", "snapshots")

RUNTIME_LOG = os.path.join(LOG_DIR, "runtime.jsonl")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SNAPSHOT_DIR, exist_ok=True)


def now():
    return datetime.utcnow().isoformat() + "Z"


def save_snapshot(snapshot: dict):

    ts = snapshot.get("timestamp", now())
    filename = ts.replace(":", "-") + ".json"

    path = os.path.join(SNAPSHOT_DIR, filename)

    with open(path, "w") as f:
        json.dump(snapshot, f, indent=2)


def build_runtime_entry(
    snapshot,
    talnir_trace,
    choice_result,
    committed_state,
    talnir_realignment,
    executor_result,
    action_taken,
    outcome
):

    entry = {
        "snapshot": snapshot,
        "talnir_trace": talnir_trace,
        "choice_result": choice_result,
        "committed_state": committed_state,
        "talnir_realignment": talnir_realignment,
        "executor_mode": executor_result.get("selected_mode"),
        "action_taken": action_taken,
        "outcome": outcome,
        "timestamp": now(),
    }

    return entry


def log_runtime(entry: dict):

    with open(RUNTIME_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
