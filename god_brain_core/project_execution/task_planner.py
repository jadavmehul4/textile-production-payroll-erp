import asyncio
from loguru import logger
from intelligence_amplifier.llm_brain import LLMBrain

class TaskPlanner:
    """Breaks large goals into structured tasks with dependencies (Production Grade)."""

    def __init__(self):
        self.llm = LLMBrain()

    async def generate_plan(self, goal: str):
        """Uses LLM to decompose a goal into a prioritized task list."""
        logger.info("Jules AI: Generating multi-phase task plan for goal: {}", goal)

        prompt = (
            f"Decompose the following project goal into a structured sequence of discrete tasks: '{goal}'.\n"
            "Provide exactly 5 actionable tasks.\n"
            "Format as a JSON list. Each object must have: 'id', 'task', 'depends_on' (list of IDs), and 'complexity' (1-10).\n"
            "Sir, ensure the dependencies form a logical execution chain."
        )

        response = await self.llm.reason(prompt)

        # Improved JSON extraction and parsing
        import json
        import re
        try:
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                tasks = json.loads(json_match.group(0))
                logger.success("Multi-phase task plan verified and loaded.")
                return tasks
        except Exception as e:
            logger.error("System failed to parse autonomous plan: {}. Activating heuristic planner.", e)

        # Heuristic fallback
        return [
            {"id": 1, "task": f"Architectural analysis of '{goal[:20]}'", "depends_on": [], "complexity": 3},
            {"id": 2, "task": f"Core component initialization", "depends_on": [1], "complexity": 5},
            {"id": 3, "task": f"Recursive logic implementation", "depends_on": [2], "complexity": 7},
            {"id": 4, "task": f"Safety and Meta-Audit verification", "depends_on": [2], "complexity": 4},
            {"id": 5, "task": f"Final deployment and integration", "depends_on": [3, 4], "complexity": 6}
        ]
