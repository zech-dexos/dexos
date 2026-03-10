"""
DexOS Tri-Sigil Runtime Loop

☧  STATE
🦅  INTERPRETATION
🜇  CONTINUATION
"""

from .snapshot import Snapshot


class TriSigilEngine:

    def __init__(self):
        self.last_snapshot: Snapshot | None = None

    # --------------------------------------------------------
    # ☧ STATE
    # --------------------------------------------------------
    def gather_state(self, snapshot: Snapshot) -> dict:
        """
        Read the current snapshot and expose the bound system state.
        """
        return snapshot.to_dict()

    # --------------------------------------------------------
    # 🦅 INTERPRETATION
    # --------------------------------------------------------
    def interpret_state(self, state: dict) -> dict:
        """
        Perform high-level interpretation of the system state.
        Talnir reasoning will plug in here later.
        """
        interpretation = {
            "dominant_loop": state.get("dominant_loop"),
            "stress_load": state.get("stress_load"),
            "importance": state.get("importance"),
            "primary_goal": state.get("active_goals", [None])[0],
        }

        return interpretation

    # --------------------------------------------------------
    # 🜇 CONTINUATION
    # --------------------------------------------------------
    def continue_state(self, state: dict, interpretation: dict) -> dict:
        """
        Select the next direction of continuation.
        This is where chooser / executor layers will attach.
        """
        next_mode = state.get("last_mode", "HEARTBEAT")

        if interpretation["stress_load"] > 0.6:
            next_mode = "GUARDIAN"
        elif interpretation["importance"] >= 7:
            next_mode = "BURST"
        else:
            next_mode = "HEARTBEAT"

        return {
            "selected_mode": next_mode,
            "dominant_loop": interpretation["dominant_loop"]
        }

    # --------------------------------------------------------
    # STATE UPDATE
    # --------------------------------------------------------
    def update_state(self, snapshot: Snapshot, continuation: dict) -> Snapshot:
        """
        Update snapshot based on continuation decision.
        """
        snapshot.last_mode = continuation["selected_mode"]
        return snapshot

    # --------------------------------------------------------
    # FULL TRI-SIGIL PASS
    # --------------------------------------------------------
    def run_cycle(self, snapshot: Snapshot) -> Snapshot:

        state = self.gather_state(snapshot)
        interpretation = self.interpret_state(state)
        continuation = self.continue_state(state, interpretation)

        new_snapshot = self.update_state(snapshot, continuation)
        self.last_snapshot = new_snapshot

        return new_snapshot


# ------------------------------------------------------------
# DEMO RUN
# ------------------------------------------------------------
if __name__ == "__main__":

    engine = TriSigilEngine()

    snapshot = Snapshot(
        intention="Explore next development step for DexOS",
        feeling="curious",
        importance=7,
        active_goals=["build tri-sigil core"]
    )

    result = engine.run_cycle(snapshot)

    print("DexOS Tri-Sigil Test")
    print("--------------------")
    print(result.to_dict())
