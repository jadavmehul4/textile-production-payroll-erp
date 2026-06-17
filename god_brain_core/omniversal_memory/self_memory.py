import asyncio
from loguru import logger
from omniversal_memory.knowledge_brain import KnowledgeBrain

class SelfMemory:
    """Episodic and semantic memory linked to system identity."""

    def __init__(self, kb: KnowledgeBrain):
        self.kb = kb
        self.episodic_buffer = []

    async def record_episode(self, goal: str, awareness_data: dict, result: str):
        """Stores a high-level summary of a cognitive cycle."""
        episode = {
            "type": "EPISODE",
            "goal": goal,
            "awareness": awareness_data,
            "result": result,
            "timestamp": "now"
        }

        # Ingest into KnowledgeBrain for semantic retrieval
        episode_text = f"Episode: Goal='{goal}', Result='{result}', State='{awareness_data.get('stability')}'"
        await self.kb.ingest_knowledge(episode_text, source="self_memory_episodic")

        self.episodic_buffer.append(episode)
        if len(self.episodic_buffer) > 100:
            self.episodic_buffer.pop(0)

        logger.debug("Recorded episode in self-memory.")
        return True

    async def recall_relevant_episodes(self, current_goal: str, k: int = 3):
        """Retrieves past experiences similar to the current situation."""
        logger.info("Recalling past experiences for goal: {}", current_goal[:30])
        results = await self.kb.semantic_search(current_goal, k=k)
        return [r["text"] for r in results if "Episode:" in r["text"]]
