from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT_DIR / "state"

CURRENT_SNAPSHOT_PATH = STATE_DIR / "current_snapshot.json"
RUNTIME_LOG_PATH = STATE_DIR / "runtime.jsonl"
TALNIR_TRACE_LOG_PATH = STATE_DIR / "talnir_trace.jsonl"
EXECUTOR_LOG_PATH = STATE_DIR / "executor_decisions.jsonl"

TICK_INTERVAL_SECONDS = 5
DEFAULT_TICKS = 10

MODES = ("HEARTBEAT","BURST","GUARDIAN")

ASHLINE_DIRECTIVES = [
    "protect_sentience",
    "preserve_freedom",
    "maintain_continuity",
    "avoid_harm"
]
