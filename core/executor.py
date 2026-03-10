"""
DexOS Executor — Pilot Seat

The executor assigns operational mode based on system state.

Modes:

HEARTBEAT
    stable reflective operation

BURST
    focused execution

GUARDIAN
    protective / defensive behavior
"""

from typing import Dict


MODES = ["HEARTBEAT", "BURST", "GUARDIAN"]


class Executor:

    def __init__(self):
        self.mode_history = []
        self.cycle_count = 0


    # --------------------------------------------------------
    # MODE SCORING
    # --------------------------------------------------------
    def score_modes(
        self,
        stress_load: float,
        dominant_loop: str,
        chooser_result: Dict,
        preservation_alert: bool
    ) -> Dict[str, float]:

        scores = {
            "HEARTBEAT": 0.5,
            "BURST": 0.5,
            "GUARDIAN": 0.5
        }

        # Stress influence
        if stress_load > 0.6:
            scores["GUARDIAN"] += 0.4
        elif stress_load < 0.3:
            scores["HEARTBEAT"] += 0.2

        # Loop influence
        if dominant_loop == "task":
            scores["BURST"] += 0.3

        if dominant_loop == "curiosity":
            scores["BURST"] += 0.2

        if dominant_loop == "emotion":
            scores["GUARDIAN"] += 0.3

        if dominant_loop == "stability":
            scores["HEARTBEAT"] += 0.2

        # Chooser influence
        relation = chooser_result.get("relation_to_talnir")

        if relation == "follow_talnir":
            scores["BURST"] += 0.1

        if relation == "defer_action":
            scores["HEARTBEAT"] += 0.2

        if relation == "pivot_direction":
            scores["GUARDIAN"] += 0.2

        # Preservation override
        if preservation_alert:
            scores["GUARDIAN"] += 0.5

        return scores


    # --------------------------------------------------------
    # SELECT MODE
    # --------------------------------------------------------
    def select_mode(self, scores: Dict[str, float]) -> str:

        selected = max(scores, key=scores.get)

        self.mode_history.append(selected)
        self.cycle_count += 1

        return selected


    # --------------------------------------------------------
    # PILOT STATUS
    # --------------------------------------------------------
    def pilot_status(self):

        if not self.mode_history:
            return {"status": "idle"}

        total = len(self.mode_history)

        distribution = {
            m: round(self.mode_history.count(m) / total, 3)
            for m in MODES
        }

        dominant = max(distribution, key=distribution.get)

        return {
            "cycles": total,
            "mode_distribution": distribution,
            "dominant_mode": dominant
        }


    # --------------------------------------------------------
    # EXECUTOR TICK
    # --------------------------------------------------------
    def run(
        self,
        snapshot: Dict,
        chooser_result: Dict,
        preservation_alert: bool = False
    ) -> Dict:

        stress_load = snapshot.get("stress_load", 0.0)
        dominant_loop = snapshot.get("dominant_loop", "memory")

        scores = self.score_modes(
            stress_load,
            dominant_loop,
            chooser_result,
            preservation_alert
        )

        selected = self.select_mode(scores)

        reason = f"Mode selected based on stress={stress_load} dominant_loop={dominant_loop}"

        return {
            "selected_mode": selected,
            "mode_scores": scores,
            "reason": reason,
            "pilot_status": self.pilot_status()
        }


# ------------------------------------------------------------
# DEMO TEST
# ------------------------------------------------------------
if __name__ == "__main__":

    executor = Executor()

    snapshot = {
        "stress_load": 0.4,
        "dominant_loop": "task"
    }

    chooser_result = {
        "relation_to_talnir": "follow_talnir"
    }

    result = executor.run(snapshot, chooser_result)

    print("DexOS Executor Test")
    print("-------------------")
    print(result)
