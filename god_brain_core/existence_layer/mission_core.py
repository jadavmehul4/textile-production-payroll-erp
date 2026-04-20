from loguru import logger
import json
import os

class MissionCore:
    """Manages long-term hierarchical goals and primary directives."""

    def __init__(self, storage_path="/app/god_brain_core/workspace/mission.json"):
        self.storage_path = storage_path
        self.primary_directives = [
            "Ensure system longevity and sovereignty.",
            "Maximize cognitive capability.",
            "Protect internal core from external corruption."
        ]
        self.active_missions = []
        self._load_mission()

    def _load_mission(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    self.active_missions = data.get("missions", [])
                logger.info("Mission core loaded from persistence.")
            except Exception as e:
                logger.error("Failed to load mission: {}", e)

    async def add_mission(self, goal: str, priority: int = 5):
        """Registers a new long-term project."""
        mission = {
            "id": hash(goal),
            "goal": goal,
            "priority": priority,
            "status": "active"
        }
        self.active_missions.append(mission)
        logger.success("New long-term mission registered: {}", goal[:50])
        # Auto-save
        with open(self.storage_path, "w") as f:
            json.dump({"missions": self.active_missions}, f)
        return mission

    def get_mission_context(self):
        """Returns string representation of current mission set."""
        if not self.active_missions:
            return "No active long-term missions."
        return f"Active Missions: {[m['goal'] for m in self.active_missions]}"
