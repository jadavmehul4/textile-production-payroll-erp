import unittest
import asyncio
from tools.logger_tool import LoggerTool

class TestTools(unittest.TestCase):
    def setUp(self):
        self.tool = LoggerTool()
        self.loop = asyncio.get_event_loop()

    def test_logger_tool(self):
        async def run_test():
            result = await self.tool.execute(message="Testing Tool", level="SUCCESS")
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["logged"], "Testing Tool")

        self.loop.run_until_complete(run_test())

if __name__ == "__main__":
    unittest.main()
