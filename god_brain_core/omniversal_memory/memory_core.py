import asyncio
from loguru import logger
from intelligence_amplifier.llm_brain import LLMBrain

class MemoryCore:
    """Handles raw experience storage and pattern-based recall."""

    def __init__(self):
        self.name = "Memory Core"
        self.llm = LLMBrain()
        self.storage = []

    async def store_experience(self, experience: str):
        """Archives a raw experience string."""
        logger.debug("Memory Core: Archiving experiential data...")
        self.storage.append(experience)
        if len(self.storage) > 1000: self.storage.pop(0)
        return True

    async def recall_context(self, query: str):
        """Retrieves textual context based on a query."""
        # Simple heuristic recall
        relevant = [s for s in self.storage if any(word in s.lower() for word in query.lower().split())]
        return " ".join(relevant[-3:]) if relevant else "No direct matches found."
