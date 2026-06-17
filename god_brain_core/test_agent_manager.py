import unittest
import asyncio
from agent_universe.agent_manager import AgentManager

class TestAgentManager(unittest.TestCase):
    def setUp(self):
        self.manager = AgentManager()
        self.loop = asyncio.get_event_loop()

    def test_coordinate(self):
        async def run_test():
            goal = "Test parallel coordination"
            proposals = await self.manager.coordinate(goal, "No context")

            # Should have at least 4 core agents + maybe 1 dynamic
            self.assertGreaterEqual(len(proposals), 4)
            for p in proposals:
                self.assertIn("agent", p)
                self.assertIn("proposal", p)
                self.assertIn("confidence", p)
                self.assertIn("risk", p)

        self.loop.run_until_complete(run_test())

if __name__ == "__main__":
    unittest.main()
