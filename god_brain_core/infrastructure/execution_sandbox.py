import asyncio
from loguru import logger
from security_omega.code_validator import CodeValidator
from security_omega.sandbox_executor import SandboxExecutor

class ExecutionSandbox:
    """Combines validation and sandbox execution for infrastructure safety."""

    def __init__(self):
        self.validator = CodeValidator()
        self.executor = SandboxExecutor()

    async def run_safely(self, code: str, arguments: dict):
        """Validates and executes code, returning the result or error."""
        logger.info("INFRA: Safety gate initiating for execution...")

        is_safe, reason = self.validator.validate(code)
        if not is_safe:
            return {"status": "rejected", "reason": reason}

        result = await self.executor.execute_tool_logic(code, arguments)
        return result
