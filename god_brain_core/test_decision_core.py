import unittest
import asyncio
from reality_engine.decision_core import DecisionCore

class TestDecisionCore(unittest.TestCase):
    def setUp(self):
        self.core = DecisionCore()
        self.loop = asyncio.get_event_loop()

    def test_synthesize(self):
        async def run_test():
            goal = "Test synthesis"
            proposals = [
                {"agent": "A", "proposal": "P1", "confidence": 0.9, "risk": 0.1},
                {"agent": "B", "proposal": "P2", "confidence": 0.7, "risk": 0.5}
            ]

            decision = await self.core.synthesize(goal, proposals)
            self.assertEqual(decision["agent_origin"], "A")
            self.assertIn("refined_action", decision)

        self.loop.run_until_complete(run_test())

if __name__ == "__main__":
    unittest.main()
