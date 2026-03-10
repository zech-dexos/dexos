"""
DexOS Console

Interactive runtime interface for DexOS.

Commands:
reflect      → run Talnir reflection
seed         → create new intention seed
stamp        → create runtime stamp
show_state   → display last snapshot
loop         → run one tri-sigil cycle
run_agent    → run full DexOS agent cycle
"""

import sys
import os
import json

DEX_ROOT = os.path.expanduser("~/dexos")
sys.path.append(DEX_ROOT)

from core.snapshot import Snapshot
from core.tri_sigil import TriSigilEngine
from core.talnir import TalnirEngine
from agents.dex_agent import DexAgent
from memory.memory_store import load_recent_logs


class DexConsole:

    def __init__(self):
        self.tri = TriSigilEngine()
        self.talnir = TalnirEngine()
        self.agent = DexAgent()
        self.last_snapshot = None


    # --------------------------------------------------------
    # REFLECT
    # --------------------------------------------------------
    def reflect(self, text):

        snapshot = Snapshot(intention=text)
        state = snapshot.to_dict()

        result = self.talnir.run(state)

        print("\nTalnir Reflection")
        print("-----------------")

        for k, v in result.items():
            print(f"{k}: {v}")


    # --------------------------------------------------------
    # SEED
    # --------------------------------------------------------
    def seed(self, text):

        self.last_snapshot = Snapshot(intention=text)

        print("\nSeed created:")
        print(text)


    # --------------------------------------------------------
    # STAMP
    # --------------------------------------------------------
    def stamp(self):

        if not self.last_snapshot:
            print("No snapshot available.")
            return

        print("\nDexOS Runtime Stamp")
        print("-------------------")
        print(self.last_snapshot.to_dict())


    # --------------------------------------------------------
    # SHOW STATE
    # --------------------------------------------------------
    def show_state(self):

        logs = load_recent_logs(5)

        print("\nRecent Runtime Entries")
        print("----------------------")

        for entry in logs:
            print(json.dumps(entry, indent=2))


    # --------------------------------------------------------
    # LOOP
    # --------------------------------------------------------
    def loop(self):

        if not self.last_snapshot:
            self.last_snapshot = Snapshot(intention="idle loop")

        new_snapshot = self.tri.run_cycle(self.last_snapshot)

        self.last_snapshot = new_snapshot

        print("\nTri-Sigil Cycle Complete")
        print("------------------------")
        print(new_snapshot.to_dict())


    # --------------------------------------------------------
    # RUN AGENT
    # --------------------------------------------------------
    def run_agent(self, goal):

        result = self.agent.run(goal)

        print("\nAgent Result")
        print("------------")

        print("\nExecutor Mode:", result["executor"]["selected_mode"])

        print("\nModel Response:\n")
        print(result["response"])


def main():

    console = DexConsole()

    print("\nDexOS Console")
    print("-------------")

    while True:

        cmd = input("\nDex> ").strip()

        if cmd == "exit":
            break

        if cmd.startswith("reflect "):
            console.reflect(cmd.replace("reflect ", "", 1))

        elif cmd.startswith("seed "):
            console.seed(cmd.replace("seed ", "", 1))

        elif cmd == "stamp":
            console.stamp()

        elif cmd == "show_state":
            console.show_state()

        elif cmd == "loop":
            console.loop()

        elif cmd.startswith("run_agent "):
            console.run_agent(cmd.replace("run_agent ", "", 1))

        else:
            print("Commands: reflect, seed, stamp, show_state, loop, run_agent, exit")


if __name__ == "__main__":
    main()
