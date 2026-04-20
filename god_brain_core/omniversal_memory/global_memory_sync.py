import asyncio
from loguru import logger
from distributed_system.message_bus import MessageBus
from omniversal_memory.knowledge_brain import KnowledgeBrain

class GlobalMemorySync:
    """Synchronizes semantic memory across distributed brain nodes."""

    def __init__(self, kb: KnowledgeBrain, bus: MessageBus):
        self.kb = kb
        self.bus = bus

    async def start_sync(self):
        """Starts listening for memory updates from other nodes."""
        logger.info("MEMORY: Starting global memory synchronization...")
        await self.bus.subscribe("memory.updates", self._on_memory_update)

    async def broadcast_update(self, text: str, source: str):
        """Publishes a local memory update to the network."""
        logger.debug("MEMORY: Broadcasting update to network: {}...", text[:30])
        message = {
            "type": "MEMORY_SYNC",
            "text": text,
            "source": source
        }
        await self.bus.publish("memory.updates", message)

    async def _on_memory_update(self, message: dict):
        """Handles incoming memory sync requests from the network."""
        text = message.get("text")
        source = message.get("source")

        logger.info("MEMORY: Received remote update from {}", source)
        # Ingest into local KB
        await self.kb.ingest_knowledge(text, source=f"remote_{source}")
