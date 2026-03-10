def talnir(snapshot):

    stress=snapshot["stress_load"]
    dom=snapshot["dominant_loop"]

    if stress>0.7:
        mode="GUARDIAN"
    elif dom=="task":
        mode="BURST"
    else:
        mode="HEARTBEAT"

    return {
        "tick_id":snapshot["tick_id"],
        "recommended_mode":mode,
        "dominant":dom,
        "stress":stress
    }
