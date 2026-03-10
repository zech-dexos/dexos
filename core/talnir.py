"""
DexOS Talnir Reasoning Engine

Talnir runs during the 🦅 INTERPRETATION phase of the Tri-Sigil loop.

It produces a structured reasoning trace answering nine questions:
- what is
- where to move
- what matters
- what resists
- what is learned
- what is reinforced
- how to continue
- what to guard
- what becomes clear
"""

from typing import Dict


class TalnirEngine:

    QUESTIONS = [
        "what_is",
        "where_to_move",
        "what_matters",
        "what_resists",
        "what_is_learned",
        "what_is_reinforced",
        "how_to_continue",
        "what_to_guard",
        "what_becomes_clear",
    ]

    def run(self, state: Dict) -> Dict:
        """
        Generate Talnir reasoning output from system state.
        This version is deterministic and structured.
        Later versions can incorporate model reasoning.
        """

        dominant_loop = state.get("dominant_loop")
        stress = state.get("stress_load", 0)
        goals = state.get("active_goals", [])
        intention = state.get("intention")

        result = {
            "what_is": f"System intention is '{intention}'. Dominant loop is '{dominant_loop}'. Stress level is {stress}.",

            "where_to_move": "Follow active goals while maintaining system stability.",

            "what_matters": f"Primary goal focus: {goals[0] if goals else 'maintain continuity'}",

            "what_resists": "Stress imbalance or conflicting loop pressures may slow progress.",

            "what_is_learned": "System behavior improves through observation of prior cycles.",

            "what_is_reinforced": "Stable loops and successful goal progress should be reinforced.",

            "how_to_continue": "Proceed with the next controlled execution step.",

            "what_to_guard": "Protect system continuity and avoid harmful or destabilizing actions.",

            "what_becomes_clear": "The system direction becomes clearer through iterative cycles."
        }

        return result


# ------------------------------------------------------------
# DEMO TEST
# ------------------------------------------------------------
if __name__ == "__main__":

    test_state = {
        "intention": "Advance DexOS architecture",
        "dominant_loop": "curiosity",
        "stress_load": 0.3,
        "active_goals": ["build Talnir engine"]
    }

    talnir = TalnirEngine()
    output = talnir.run(test_state)

    print("DexOS Talnir Test")
    print("-----------------")

    for k, v in output.items():
        print(f"{k}: {v}")
