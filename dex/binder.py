from datetime import datetime, timezone

def bind(loop_outputs,state,tick):

    pressures={k:v["pressure"] for k,v in loop_outputs.items()}
    dominant=max(pressures,key=pressures.get)

    stress=sum(pressures.values())/len(pressures)

    return {
        "timestamp":datetime.now(timezone.utc).isoformat(),
        "tick_id":tick,
        "intention":state.get("intention","build system"),
        "last_mode":state.get("last_mode","HEARTBEAT"),
        "loop_pressures":pressures,
        "stress_load":stress,
        "dominant_loop":dominant
    }
