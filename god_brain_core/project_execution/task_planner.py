import asyncio
from loguru import logger
from intelligence_amplifier.llm_brain import LLMBrain

class TaskPlanner:
    """Breaks large goals into structured tasks with dependencies."""

    def __init__(self):
        self.llm = LLMBrain()

    async def generate_plan(self, goal: str):
        """Uses LLM to decompose a goal into a prioritized task list."""
        logger.info("Generating task plan for goal: {}", goal)

        prompt = (
            f"Decompose the following large-scale project goal into 5-8 discrete, actionable tasks: '{goal}'.\n"
            "Format each task as a JSON object with 'id', 'task', 'depends_on' (list of IDs), and 'estimated_complexity' (1-10).\n"
            "Return ONLY the JSON list of tasks."
        )

        # In simulation mode, we provide a deterministic mock plan
        if not self.llm.client:
            tasks = [
                {"id": 1, "task": f"Phase 1: Architecture Design for {goal[:20]}", "depends_on": [], "complexity": 3},
                {"id": 2, "task": f"Phase 2: Core Module Implementation", "depends_on": [1], "complexity": 5},
                {"id": 3, "task": f"Phase 3: Integration and Networking", "depends_on": [2], "complexity": 7},
                {"id": 4, "task": f"Phase 4: Safety Protocol Activation", "depends_on": [2], "complexity": 4},
                {"id": 5, "task": f"Phase 5: Final Validation and Deployment", "depends_on": [3, 4], "complexity": 6}
            ]
        else:
            response = await self.llm.reason(prompt)
            # Attempt to parse JSON from LLM response
            import json
            import re
            try:
                # Extract json block if present
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                tasks = json.loads(json_match.group(0)) if json_match else []
            except Exception as e:
                logger.error("Failed to parse LLM plan: {}. Using fallback.", e)
                tasks = [{"id": 1, "task": "Initial Research", "depends_on": [], "complexity": 1}]

        logger.success("Generated plan with {} tasks.", len(tasks))
        return tasks
