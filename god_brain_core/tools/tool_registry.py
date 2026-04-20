import os
import importlib.util
from loguru import logger
from tools.base_tool import BaseTool

class ToolRegistry:
    """Dynamically loads and manages all system tools (Jules AI Optimized)."""

    def __init__(self):
        self.tools = {}
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.generated_dir = os.path.join(self.base_dir, "generated")

    def discover_tools(self):
        """Loads all tools from static and generated directories."""
        logger.info("Jules AI: Syncing system capabilities...")

        # Load core tools
        from tools.logger_tool import LoggerTool
        from tools.web_search_tool import WebSearchTool
        from tools.file_system_tool import FileSystemTool
        from tools.api_tool import APITool
        from tools.adb_bridge import ADBBridge
        from tools.kernel_bridge import KernelBridge

        self.register_tool(LoggerTool())
        self.register_tool(WebSearchTool())
        self.register_tool(FileSystemTool())
        self.register_tool(APITool())
        self.register_tool(ADBBridge())
        self.register_tool(KernelBridge())

        # Load generated tools
        if os.path.exists(self.generated_dir):
            for filename in os.listdir(self.generated_dir):
                if filename.startswith("tool_") and filename.endswith(".py"):
                    self._load_from_file(os.path.join(self.generated_dir, filename))

        logger.success("Capability sync complete. SIR, I am ready.")

    def _load_from_file(self, filepath: str):
        """Dynamically imports a tool from a file."""
        try:
            module_name = os.path.basename(filepath)[:-3]
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for attr in dir(module):
                cls = getattr(module, attr)
                if isinstance(cls, type) and issubclass(cls, BaseTool) and cls is not BaseTool:
                    self.register_tool(cls())
        except Exception as e:
            logger.error("Failed to load capability from {}: {}", filepath, e)

    def register_tool(self, tool: BaseTool):
        """Registers a tool instance."""
        self.tools[tool.name] = tool
        logger.debug("Registered system tool: {}", tool.name)

    def get_tool(self, name: str):
        """Retrieves a tool by name."""
        return self.tools.get(name)

    def list_tools(self):
        """Lists all registered tool names and descriptions."""
        return {name: tool.description for name, tool in self.tools.items()}
