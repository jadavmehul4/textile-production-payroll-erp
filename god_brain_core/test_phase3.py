import unittest
import asyncio
from hyper_meta_cognition.self_reflection_engine import SelfReflectionEngine

class TestPhase3Engines(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()

    def test_reflection(self):
        async def run_test():
            engine = SelfReflectionEngine()
            result = await engine.reflect("Goal", {"decision": "D"}, {"status": "success"})
            self.assertIn("error", result)
            self.assertIn("improvement", result)
        self.loop.run_until_complete(run_test())

    def test_memory_evolution(self):
        async def run_test():
            from omniversal_memory.knowledge_brain import KnowledgeBrain
            from omniversal_memory.memory_evolution_engine import MemoryEvolutionEngine
            kb = KnowledgeBrain()
            await kb.ingest_knowledge("M1")
            await kb.ingest_knowledge("M2")
            engine = MemoryEvolutionEngine(kb)
            result = await engine.evolve_memory()
            self.assertTrue(result)
        self.loop.run_until_complete(run_test())

if __name__ == "__main__":
    unittest.main()
