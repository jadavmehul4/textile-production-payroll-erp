import asyncio
from loguru import logger
from intelligence_amplifier.llm_brain import LLMBrain

class SelfAwarenessEngine:
    """Monitors system internal state and outputs structured awareness data."""

    def __init__(self, identity_core, progress_tracker=None):
        self.identity = identity_core
        self.tracker = progress_tracker
        self.llm = LLMBrain()

    async def generate_awareness_report(self):
        """Compiles internal metrics into a cohesive self-awareness state."""
        logger.info("Generating system self-awareness report...")

        traits = self.identity.identity.get("personality_traits", {})
        progress = self.tracker.get_completion_percentage() if self.tracker else 0.0

        # Simple simulated awareness logic
        # In a full impl, this might query all modules for 'how are you doing?'
        awareness = {
            "status": "Healthy",
            "stability": 0.95,
            "confidence": 0.88,
            "traits": traits,
            "current_progress": progress,
            "self_description": f"I am {self.identity.identity['name']} (v{self.identity.identity['version']}). My current confidence is high."
        }

        # Optionally refine with LLM
        prompt = f"Given these system metrics: {awareness}, provide a one-sentence internal monologue summarizing your current state of being."
        monologue = await self.llm.reason(prompt)
        awareness["monologue"] = monologue

        logger.success("Self-Awareness: {}", awareness["monologue"][:60])
        return awareness
