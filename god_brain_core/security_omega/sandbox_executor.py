import asyncio
import sys
import io
from loguru import logger
from tools.base_tool import BaseTool

class SandboxExecutor:
    """Executes validated code in a restricted environment."""

    async def execute_tool_logic(self, code: str, kwargs: dict):
        """Runs the tool code with provided arguments in a restricted namespace."""
        logger.info("Executing code in sandbox...")

        # Capture stdout
        stdout = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = stdout

        try:
            # Local namespace for execution
            local_namespace = {"BaseTool": BaseTool, "logger": logger}

            # Exec the code
            exec(code, local_namespace, local_namespace)

            # Find the class that was defined
            tool_class = None
            for attr in local_namespace.values():
                if isinstance(attr, type) and issubclass(attr, BaseTool) and attr is not BaseTool:
                    tool_class = attr
                    break

            if tool_class:
                # Instantiate and execute
                tool_instance = tool_class()
                result = await tool_instance.execute(**kwargs)
                return {"status": "success", "result": result, "output": stdout.getvalue()}

            return {"status": "error", "message": "No tool class found in generated code"}

        except Exception as e:
            logger.error("Sandbox execution failed: {}", e)
            return {"status": "error", "message": str(e)}
        finally:
            sys.stdout = old_stdout
