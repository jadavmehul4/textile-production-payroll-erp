import os
import hashlib
from loguru import logger
from agent_universe.base_agent import BaseAgent

class CoderAgent(BaseAgent):
    """
    Responsibilities:
    - Generate Python tool code using LLMBrain
    - Follow strict tool template
    - Output structured code
    """
    def __init__(self):
        super().__init__(name="Coder-01", role="System Architect & Coder")
        # Template with better indentation management
        self.template = """from tools.base_tool import BaseTool
from loguru import logger

class {class_name}(BaseTool):
    def __init__(self):
        super().__init__(
            name="{tool_name}",
            description="{description}"
        )

    async def execute(self, **kwargs):
        # Implementation
{implementation}
        return {{"status": "success", "data": "Tool executed successfully"}}
"""

    async def generate_tool(self, tool_requirement: str):
        """Generates a new Python tool based on requirements."""
        logger.info("Generating new tool for requirement: {}", tool_requirement)

        if not self.llm.client:
            # Better mock implementation for simulation
            implementation = "        logger.info('Executing simulated tool logic')\n        pass"
        else:
            prompt = (
                f"Generate a Python implementation for a tool that satisfies this requirement: '{tool_requirement}'.\n"
                "Respond ONLY with the Python code for the 'execute' method body. Do not include class definition.\n"
                "Focus on pure logic. No restricted imports (os, sys, etc.).\n"
                "Indentation: Start with 8 spaces."
            )
            implementation = await self.llm.reason(prompt)

        # Clean up implementation if LLM added markdown backticks
        if "```python" in implementation:
            implementation = implementation.split("```python")[1].split("```")[0]
        elif "```" in implementation:
            implementation = implementation.split("```")[1].split("```")[0]

        tool_name = f"GeneratedTool_{hashlib.md5(tool_requirement.encode()).hexdigest()[:8]}"
        class_name = tool_name
        description = f"Self-generated tool for: {tool_requirement}"

        # Ensure implementation has proper indentation if it doesn't
        if not implementation.startswith("        "):
            lines = implementation.split("\n")
            implementation = "\n".join(["        " + line if line.strip() else line for line in lines])

        code = self.template.format(
            class_name=class_name,
            tool_name=tool_name,
            description=description,
            implementation=implementation
        )

        return {
            "name": tool_name,
            "code": code,
            "description": description
        }

    async def save_tool(self, tool_data: dict):
        """Saves the generated tool to the tools/generated directory."""
        filename = f"tool_{hashlib.md5(tool_data['name'].encode()).hexdigest()[:8]}.py"
        filepath = os.path.join("tools", "generated", filename)

        # Ensure directory exists relative to current working dir
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w") as f:
            f.write(tool_data["code"])

        logger.success("Tool saved to {}", filepath)
        return filepath
