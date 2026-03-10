#!/usr/bin/env python3

"""
DexOS Runtime Launcher

Flow:

prompt
→ snapshot
→ Talnir
→ chooser
→ Talnir realign
→ executor
→ model
→ memory write
"""

import sys
import os

DEX_ROOT = os.path.expanduser("~/dexos")
sys.path.append(DEX_ROOT)

from agents.dex_agent import DexAgent


def main():

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python run_dexos.py 'your goal here'")
        return

    goal = sys.argv[1]

    agent = DexAgent()

    result = agent.run(goal)

    print("\n========================")
    print("DEXOS RUN COMPLETE")
    print("========================")

    print("\nGoal:")
    print(goal)

    print("\nExecutor Mode:")
    print(result["executor"]["selected_mode"])

    print("\nModel Output:")
    print(result["response"])


if __name__ == "__main__":
    main()
