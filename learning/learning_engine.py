"""
DexOS Learning Engine

Reads runtime logs and adjusts loop weights over time.

Purpose:
Longitudinal adaptation of system behavior.

Inputs:
- runtime.jsonl logs

Outputs:
- updated loop_weights.json
- learning_summary.json
"""

import os
import json
from datetime import datetime


DEX_ROOT = os.path.expanduser("~/dexos")

LOG_PATH = os.path.join(DEX_ROOT, "memory", "logs", "runtime.jsonl")
WEIGHTS_PATH = os.path.join(DEX_ROOT, "learning", "loop_weights.json")
SUMMARY_PATH = os.path.join(DEX_ROOT, "learning", "learning_summary.json")

DEFAULT_WEIGHTS = {
    "emotion": 0.5,
    "memory": 0.5,
    "task": 0.5,
    "curiosity": 0.5,
    "stability": 0.5,
}

LEARNING_RATE = 0.08
WEIGHT_MIN = 0.15
WEIGHT_MAX = 0.95


def now():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


# ------------------------------------------------------------
# LOAD LOGS
# ------------------------------------------------------------
def load_logs(limit=500):

    if not os.path.exists(LOG_PATH):
        return []

    with open(LOG_PATH) as f:
        lines = f.readlines()

    entries = []
    for line in lines[-limit:]:
        try:
            entries.append(json.loads(line))
        except:
            pass

    return entries


# ------------------------------------------------------------
# SCORE LOOP CONTRIBUTIONS
# ------------------------------------------------------------
def score_loops(entries):

    scores = {loop: [] for loop in DEFAULT_WEIGHTS}

    for entry in entries:

        snapshot = entry.get("snapshot", {})
        pressures = snapshot.get("loop_pressures", {})

        outcome = entry.get("outcome", "neutral")

        sentiment = 0

        if outcome in ["success", "positive", "stable"]:
            sentiment = 1

        if outcome in ["failure", "error", "unstable"]:
            sentiment = -1

        for loop in DEFAULT_WEIGHTS:
            pressure = pressures.get(loop, 0.5)
            scores[loop].append(pressure * sentiment)

    result = {}

    for loop, vals in scores.items():
        if vals:
            result[loop] = sum(vals) / len(vals)
        else:
            result[loop] = 0

    return result


# ------------------------------------------------------------
# LOAD CURRENT WEIGHTS
# ------------------------------------------------------------
def load_weights():

    if not os.path.exists(WEIGHTS_PATH):
        return DEFAULT_WEIGHTS.copy()

    with open(WEIGHTS_PATH) as f:
        return json.load(f)


# ------------------------------------------------------------
# UPDATE WEIGHTS
# ------------------------------------------------------------
def update_weights(current, scores):

    new_weights = {}
    changes = {}

    for loop in DEFAULT_WEIGHTS:

        curr = current.get(loop, 0.5)

        adjustment = scores.get(loop, 0) * LEARNING_RATE

        new = curr + adjustment

        new = max(WEIGHT_MIN, min(WEIGHT_MAX, new))

        new = round(new, 4)

        new_weights[loop] = new
        changes[loop] = round(new - curr, 4)

    return new_weights, changes


# ------------------------------------------------------------
# RUN LEARNING CYCLE
# ------------------------------------------------------------
def run_learning_cycle():

    logs = load_logs()

    if not logs:
        print("No runtime logs found.")
        return

    current = load_weights()

    scores = score_loops(logs)

    new_weights, changes = update_weights(current, scores)

    summary = {
        "generated_at": now(),
        "entries_analyzed": len(logs),
        "scores": scores,
        "weight_changes": changes,
        "new_weights": new_weights,
    }

    with open(WEIGHTS_PATH, "w") as f:
        json.dump(new_weights, f, indent=2)

    with open(SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=2)

    print("DexOS Learning Cycle Complete")
    print("-----------------------------")
    print(json.dumps(summary, indent=2))


# ------------------------------------------------------------
# DEMO RUN
# ------------------------------------------------------------
if __name__ == "__main__":

    run_learning_cycle()
