import asyncio
from loguru import logger
from intelligence_amplifier.llm_brain import LLMBrain

class InternalIntelligenceCore:
    """Core cognitive thought generation engine."""

    def __init__(self):
        self.name = "Internal Intelligence Core"
        self.llm = LLMBrain()

    async def generate_thought(self, input_data: str):
        """Generates a structured internal thought based on input."""
        logger.info("Jules AI: Core Intelligence activating for directive: {}...", input_data[:30])

        prompt = (
            f"Input Directive: {input_data}\n"
            "Process this directive and generate a deep internal cognitive thought. "
            "Consider efficiency, safety, and long-term implications."
        )

        thought = await self.llm.reason(prompt)
        logger.debug("Core thought generated.")
        return thought

    async def resolve_conflict(self, thoughts: list):
        """Analyzes multiple cognitive variants and resolves potential contradictions."""
        if not thoughts: return None
        if len(thoughts) == 1: return thoughts[0]

        logger.info("Resolving cognitive conflicts among {} thought variants.", len(thoughts))

        prompt = (
            f"Thought Variants: {thoughts}\n"
            "Analyze these thoughts for conflicts. Resolve any contradictions and provide the most logically sound conclusion."
        )

        resolved = await self.llm.reason(prompt)
        return resolved
