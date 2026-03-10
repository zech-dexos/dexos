import time

from dex.config import *
from dex.utils import *
from dex.binder import bind
from dex.talnir import talnir
from dex.executor import execute

from dex.loops.task import task_loop
from dex.loops.memory import memory_loop
from dex.loops.emotion import emotion_loop
from dex.loops.curiosity import curiosity_loop
from dex.loops.stability import stability_loop

def default_state():

    return {
        "intention":"build dexos",
        "last_mode":"HEARTBEAT"
    }

def run_tick(tick):

    state=load_json(CURRENT_SNAPSHOT_PATH,default_state())

    loops={
        "task":task_loop(state),
        "memory":memory_loop(state),
        "emotion":emotion_loop(state),
        "curiosity":curiosity_loop(state),
        "stability":stability_loop(state)
    }

    snapshot=bind(loops,state,tick)

    trace=talnir(snapshot)

    decision=execute(trace)

    snapshot["last_mode"]=decision["chosen_mode"]

    write_json(CURRENT_SNAPSHOT_PATH,snapshot)
    append_jsonl(RUNTIME_LOG_PATH,snapshot)
    append_jsonl(TALNIR_TRACE_LOG_PATH,trace)
    append_jsonl(EXECUTOR_LOG_PATH,decision)

    return snapshot,trace,decision
