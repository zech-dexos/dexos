from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


def now():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


DEFAULT_LOOP_PRESSURES = {
    "emotion": 0.5,
    "memory": 0.5,
    "task": 0.5,
    "curiosity": 0.5,
    "stability": 0.5,
}


@dataclass
class Snapshot:
    """
    Represents the bound present state of DexOS.
    This object is what the Tri-Sigil loop reads each cycle.
    """

    timestamp: str = field(default_factory=now)

    intention: str = ""
    last_mode: str = "HEARTBEAT"
    feeling: str = "neutral"
    importance: int = 5

    loop_pressures: Dict[str, float] = field(
        default_factory=lambda: DEFAULT_LOOP_PRESSURES.copy()
    )

    memory_refs: List[str] = field(default_factory=list)
    active_goals: List[str] = field(default_factory=list)

    ashline_directives: List[str] = field(default_factory=lambda: [
        "protect_sentience",
        "preserve_freedom",
        "maintain_continuity",
        "avoid_harm"
    ])

    def stress_load(self) -> float:
        """
        Measures system stress from loop pressure imbalance.
        """
        deviations = [abs(v - 0.5) for v in self.loop_pressures.values()]
        return round(sum(deviations) / len(deviations), 3)

    def dominant_loop(self) -> str:
        return max(self.loop_pressures, key=lambda k: self.loop_pressures[k])

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "intention": self.intention,
            "last_mode": self.last_mode,
            "feeling": self.feeling,
            "importance": self.importance,
            "loop_pressures": self.loop_pressures,
            "memory_refs": self.memory_refs,
            "active_goals": self.active_goals,
            "ashline_directives": self.ashline_directives,
            "stress_load": self.stress_load(),
            "dominant_loop": self.dominant_loop(),
        }
