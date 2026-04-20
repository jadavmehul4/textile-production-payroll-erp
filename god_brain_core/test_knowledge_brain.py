import unittest
import asyncio
import numpy as np
from omniversal_memory.knowledge_brain import KnowledgeBrain

class TestKnowledgeBrain(unittest.TestCase):
    def setUp(self):
        self.knowledge = KnowledgeBrain(dimension=1536)
        self.loop = asyncio.get_event_loop()

    def test_ingest_and_search(self):
        async def run_test():
            text = "Ω GOD_BRAIN_CORE_Ω is a sovereign system."
            await self.knowledge.ingest_knowledge(text, source="test")

            # Since we are in simulation mode (no API key), it uses mock embeddings.
            # Semantic search might not be truly semantic, but it should return results.
            results = await self.knowledge.semantic_search("GOD_BRAIN", k=1)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["text"], text)

        self.loop.run_until_complete(run_test())

if __name__ == "__main__":
    unittest.main()
