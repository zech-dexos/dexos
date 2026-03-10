import sys
import os

DEX_ROOT = os.path.expanduser("~/dexos")
sys.path.append(DEX_ROOT)

from core.snapshot import Snapshot
from core.talnir import TalnirEngine
from core.chooser import ChooserEngine
from core.executor import Executor
from models.ollama_adapter import OllamaAdapter
from memory.memory_store import log_runtime, save_snapshot, build_runtime_entry


def commit_choice_to_state(snapshot: dict, choice: dict) -> dict:
    """
    Commit the chooser's decision into the live runtime state.

    The chosen direction becomes the operating center.
    The original intention becomes historical context.
    """
    committed = dict(snapshot)

    committed["original_intention"] = snapshot.get("intention")
    committed["active_direction"] = choice["chosen_direction"]
    committed["active_goals"] = [choice["chosen_direction"]]
    committed["goal_relation"] = choice.get("relation_to_talnir", "aligned")
    committed["decision"] = choice.get("decision")
    committed["decision_reason"] = choice.get("reason")

    # The active intention becomes the chosen direction
    committed["intention"] = choice["chosen_direction"]

    return committed


class DexAgent:

    def __init__(self):

        self.talnir = TalnirEngine()
        self.chooser = ChooserEngine()
        self.executor = Executor()
        self.model = OllamaAdapter()


    def run(self, goal: str):

        # ----------------------------------------------------
        # SNAPSHOT
        # ----------------------------------------------------
        snapshot = Snapshot(
            intention=goal,
            active_goals=[goal]
        )

        state = snapshot.to_dict()

        # ----------------------------------------------------
        # TALNIR PROPOSAL
        # ----------------------------------------------------
        talnir_trace = self.talnir.run(state)

        # ----------------------------------------------------
        # CHOOSER DECISION
        # ----------------------------------------------------
        choice = self.chooser.choose(
            talnir_output=talnir_trace,
            memory=[],
            active_goals=[goal],
            ashline_directives=snapshot.ashline_directives,
            preservation_rules=["avoid_harm"],
            loop_pressures=snapshot.loop_pressures
        )

        # ----------------------------------------------------
        # COMMIT CHOICE INTO LIVE STATE
        # ----------------------------------------------------
        committed_state = commit_choice_to_state(state, choice)

        # ----------------------------------------------------
        # TALNIR REALIGNMENT (SECOND PASS)
        # ----------------------------------------------------
        talnir_realignment = self.talnir.run(committed_state)

        # ----------------------------------------------------
        # EXECUTOR MODE SELECTION
        # ----------------------------------------------------
        executor_result = self.executor.run(
            snapshot=committed_state,
            chooser_result=choice
        )

        # ----------------------------------------------------
        # MODEL PROMPT (USES COMMITTED STATE)
        # ----------------------------------------------------
        prompt = f"""
Active Direction:
{committed_state["intention"]}

Original Prompt:
{committed_state.get("original_intention")}

Talnir Realigned Reasoning:
{talnir_realignment}

Executor Mode:
{executor_result["selected_mode"]}

Respond with the next controlled step.
"""

        response = self.model.generate(prompt)

        # ----------------------------------------------------
        # MEMORY + LOGGING
        # ----------------------------------------------------
        entry = build_runtime_entry(
            snapshot=state,
            talnir_trace=talnir_trace,
            choice_result=choice,
            committed_state=committed_state,
            talnir_realignment=talnir_realignment,
            executor_result=executor_result,
            action_taken="model_generation",
            outcome="success"
        )

        save_snapshot(committed_state)
        log_runtime(entry)

        return {
            "goal": goal,
            "committed_direction": committed_state["intention"],
            "executor": executor_result,
            "response": response
        }


if __name__ == "__main__":

    goal = sys.argv[1] if len(sys.argv) > 1 else "Explore DexOS improvement"

    agent = DexAgent()
    result = agent.run(goal)

    print("\n========================")
    print("DEXOS RUN COMPLETE")
    print("========================\n")

    print("Original Goal:")
    print(result["goal"])

    print("\nCommitted Direction:")
    print(result["committed_direction"])

    print("\nExecutor Mode:")
    print(result["executor"]["selected_mode"])

    print("\nModel Output:\n")
    print(result["response"])
