import unittest
import asyncio
import os
from existence_layer.identity_core import IdentityCore
from hyper_meta_cognition.self_awareness_engine import SelfAwarenessEngine
from existence_layer.personality_engine import PersonalityEngine

class TestPhase8(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.identity = IdentityCore(storage_path="/app/god_brain_core/workspace/test_identity.json")

    def tearDown(self):
        if os.path.exists("/app/god_brain_core/workspace/test_identity.json"):
            os.remove("/app/god_brain_core/workspace/test_identity.json")

    def test_identity_persistence(self):
        async def run_test():
            self.identity.identity["name"] = "TestAI"
            await self.identity.save_identity()

            new_core = IdentityCore(storage_path="/app/god_brain_core/workspace/test_identity.json")
            self.assertEqual(new_core.identity["name"], "TestAI")
        self.loop.run_until_complete(run_test())

    def test_self_awareness(self):
        async def run_test():
            engine = SelfAwarenessEngine(self.identity)
            report = await engine.generate_awareness_report()
            self.assertIn("stability", report)
            self.assertIn("monologue", report)
        self.loop.run_until_complete(run_test())

    def test_personality_influence(self):
        async def run_test():
            engine = PersonalityEngine(self.identity)
            # High cautious trait should increase multiplier
            self.identity.identity["personality_traits"]["cautious"] = 1.0
            proposals = [{"agent": "A", "risk": 0.5}]
            adjusted = await engine.influence_decision_weight(proposals)
            self.assertGreater(adjusted[0]["risk_penalty_multiplier"], 1.0)
        self.loop.run_until_complete(run_test())

if __name__ == "__main__":
    unittest.main()
