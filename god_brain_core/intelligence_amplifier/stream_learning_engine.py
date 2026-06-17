import asyncio
from loguru import logger
from intelligence_amplifier.llm_brain import LLMBrain

class StreamLearningEngine:
    """Continuous background learning from system data streams."""

    def __init__(self):
        self.llm = LLMBrain()
        self.learning_buffer = []

    async def ingest_stream_data(self, data: str):
        """Adds new information to the continuous learning stream."""
        logger.debug("Jules AI: Ingesting telemetry into stream learning buffer...")
        self.learning_buffer.append(data)
        if len(self.learning_buffer) > 10:
            await self._trigger_learning_cycle()

    async def _trigger_learning_cycle(self):
        """Analyzes the stream buffer to extract new insights or parameter updates."""
        logger.info("Jules AI: Triggering autonomous stream learning cycle for {} items...", len(self.learning_buffer))

        prompt = (
            f"Telemetry Stream Data: {self.learning_buffer}\n"
            "Analyze this stream of system events. Identify any recurring performance patterns "
            "or potential for algorithmic optimization. Respond with one actionable insight."
        )

        insight = await self.llm.reason(prompt)
        logger.success("Stream learning optimization complete: {}", insight[:60])

        self.learning_buffer = []
        return insight
