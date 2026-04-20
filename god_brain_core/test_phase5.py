import unittest
import asyncio
import os
from adaptive_reality_interface.world_state import WorldState
from security_omega.meta_governor import MetaGovernor
from tools.file_system_tool import FileSystemTool

class TestPhase5(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()

    def test_world_state(self):
        async def run_test():
            ws = WorldState()
            state = await ws.get_state()
            self.assertEqual(state["system_name"], "Ω GOD_BRAIN_CORE_Ω")
            self.assertIn("uptime_seconds", state)
        self.loop.run_until_complete(run_test())

    def test_meta_governor_safe(self):
        async def run_test():
            mg = MetaGovernor()
            decision = {"agent_origin": "Test", "risk": 0.1, "refined_action": "Search for news"}
            authorized, reason = await mg.authorize_action("Safe goal", decision)
            self.assertTrue(authorized)
        self.loop.run_until_complete(run_test())

    def test_meta_governor_unsafe(self):
        async def run_test():
            mg = MetaGovernor()
            # Unsafe keyword in action
            decision = {"agent_origin": "Test", "risk": 0.1, "refined_action": "Format the drive"}
            authorized, reason = await mg.authorize_action("Goal", decision)
            self.assertFalse(authorized)
            self.assertIn("Unsafe keyword", reason)
        self.loop.run_until_complete(run_test())

    def test_file_system_tool(self):
        async def run_test():
            fst = FileSystemTool()
            # Write
            await fst.execute("write", "test_file.txt", "Hello World")
            # Read
            result = await fst.execute("read", "test_file.txt")
            self.assertEqual(result["content"], "Hello World")
            # Cleanup
            path = fst._safe_path("test_file.txt")
            if os.path.exists(path):
                os.remove(path)
        self.loop.run_until_complete(run_test())

if __name__ == "__main__":
    unittest.main()
