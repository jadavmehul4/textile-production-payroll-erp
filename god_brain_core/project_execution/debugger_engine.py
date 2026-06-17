import asyncio
from loguru import logger
from intelligence_amplifier.llm_brain import LLMBrain

class DebuggerEngine:
    """Analyzes failures and suggests fixes."""

    def __init__(self):
        self.llm = LLMBrain()

    async def debug_failure(self, task: dict, error: str):
        """Analyzes an error and provides a correction strategy."""
        logger.info("Debugger analyzing failure for task: {}", task.get("task"))

        prompt = (
            f"The following task failed during execution: '{task.get('task')}'\n"
            f"Error details: {error}\n"
            "Analyze the cause and provide a specific correction strategy to fix this and retry."
        )

        analysis = await self.llm.reason(prompt)
        logger.warning("Debugger suggestion: {}", analysis[:100])

        return {
            "retry_recommended": True,
            "strategy": analysis,
            "can_auto_fix": "simple" in analysis.lower()
        }

    async def log_fix(self, task_id: int, fix: str):
        """Records the applied fix to prevent recurring errors."""
        logger.info("Applying fix for task {}: {}", task_id, fix[:50])
        return True
