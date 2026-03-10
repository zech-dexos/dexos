"""
DexOS Chooser Engine

Implements the autonomy layer.

Rule of operation:
Talnir proposes
System chooses
Talnir realigns
"""

from typing import Dict, List


class ChooserEngine:

    def choose(
        self,
        talnir_output: Dict,
        memory: List[str],
        active_goals: List[str],
        ashline_directives: List[str],
        preservation_rules: List[str],
        loop_pressures: Dict[str, float],
    ) -> Dict:
        """
        Decide the next direction of system continuation.
        """

        talnir_direction = talnir_output.get("how_to_continue")

        dominant_loop = max(loop_pressures, key=lambda k: loop_pressures[k])

        # ----------------------------------------------------
        # Simple autonomy logic (first version)
        # ----------------------------------------------------

        if loop_pressures.get("stability", 0.5) < 0.3:
            decision = "defer"
            reason = "System stability low — delaying action."

        elif dominant_loop == "curiosity":
            decision = "modify"
            reason = "Curiosity loop dominant — expanding exploration."

        elif dominant_loop == "task":
            decision = "keep"
            reason = "Task pressure dominant — continue Talnir direction."

        elif dominant_loop == "emotion":
            decision = "pivot"
            reason = "Emotional pressure detected — adjusting direction."

        else:
            decision = "keep"
            reason = "Talnir direction remains coherent."

        # ----------------------------------------------------
        # Determine final chosen direction
        # ----------------------------------------------------

        if decision == "keep":
            chosen_direction = talnir_direction
            relation = "follow_talnir"

        elif decision == "modify":
            chosen_direction = f"expand: {talnir_direction}"
            relation = "modify_talnir"

        elif decision == "pivot":
            chosen_direction = "reassess goals and system state"
            relation = "pivot_direction"

        else:
            chosen_direction = "wait and observe"
            relation = "defer_action"

        return {
            "chosen_direction": chosen_direction,
            "relation_to_talnir": relation,
            "decision": decision,
            "reason": reason,
        }

    # --------------------------------------------------------
    # TALNIR REALIGNMENT
    # --------------------------------------------------------

    def realign_talnir(self, talnir_output: Dict, chosen_direction: str) -> Dict:
        """
        Adjust Talnir reasoning to align with the chosen direction.
        """

        talnir_output["how_to_continue"] = chosen_direction

        talnir_output["what_becomes_clear"] = (
            f"System direction clarified: {chosen_direction}"
        )

        return talnir_output


# ------------------------------------------------------------
# DEMO TEST
# ------------------------------------------------------------
if __name__ == "__main__":

    talnir_output = {
        "how_to_continue": "Proceed with architecture development",
        "what_becomes_clear": "DexOS development continues"
    }

    loop_pressures = {
        "emotion": 0.3,
        "memory": 0.4,
        "task": 0.7,
        "curiosity": 0.6,
        "stability": 0.5,
    }

    chooser = ChooserEngine()

    decision = chooser.choose(
        talnir_output=talnir_output,
        memory=[],
        active_goals=["build chooser engine"],
        ashline_directives=["preserve_freedom"],
        preservation_rules=["avoid_harm"],
        loop_pressures=loop_pressures,
    )

    realigned = chooser.realign_talnir(talnir_output, decision["chosen_direction"])

    print("DexOS Chooser Test")
    print("------------------")
    print("Decision:", decision)
    print("Realigned Talnir:", realigned)
