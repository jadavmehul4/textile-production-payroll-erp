import unittest
import asyncio
from security_omega.code_validator import CodeValidator
from security_omega.sandbox_executor import SandboxExecutor
from tools.tool_registry import ToolRegistry

class TestPhase4Safety(unittest.TestCase):
    def setUp(self):
        self.validator = CodeValidator()
        self.executor = SandboxExecutor()
        self.loop = asyncio.get_event_loop()

    def test_validation_safe(self):
        code = "class TestTool: pass"
        is_safe, reason = self.validator.validate(code)
        self.assertTrue(is_safe)

    def test_validation_unsafe_import(self):
        code = "import os\nos.system('ls')"
        is_safe, reason = self.validator.validate(code)
        self.assertFalse(is_safe)
        self.assertIn("Restricted import", reason)

    def test_validation_unsafe_call(self):
        code = "eval('1+1')"
        is_safe, reason = self.validator.validate(code)
        self.assertFalse(is_safe)
        self.assertIn("Restricted keyword", reason)

    def test_sandbox_execution(self):
        async def run_test():
            code = """
from tools.base_tool import BaseTool
class MyTool(BaseTool):
    def __init__(self):
        super().__init__("MyTool", "Desc")
    async def execute(self, val=10):
        return val * 2
"""
            result = await self.executor.execute_tool_logic(code, {"val": 5})
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["result"], 10)
        self.loop.run_until_complete(run_test())

if __name__ == "__main__":
    unittest.main()
