import os
from loguru import logger
from tools.base_tool import BaseTool

class FileSystemTool(BaseTool):
    """Restricted file system tool for workspace operations."""

    def __init__(self):
        self.workspace = "/app/god_brain_core/workspace/"
        os.makedirs(self.workspace, exist_ok=True)
        super().__init__(
            name="FileSystemTool",
            description=f"Supports read, write, and list operations within {self.workspace}"
        )

    def _safe_path(self, filename: str):
        # Prevent path traversal
        clean_name = os.path.basename(filename)
        return os.path.join(self.workspace, clean_name)

    async def execute(self, operation: str, filename: str, content: str = None):
        """Executes file system operations: read, write, list."""
        logger.info("FileSystem operation: {} on {}", operation, filename)

        path = self._safe_path(filename)

        try:
            if operation.lower() == "write":
                with open(path, "w") as f:
                    f.write(content or "")
                logger.success("Successfully wrote to {}", filename)
                return {"status": "success", "file": filename}

            elif operation.lower() == "read":
                if not os.path.exists(path):
                    return {"status": "error", "message": "File not found"}
                with open(path, "r") as f:
                    data = f.read()
                return {"status": "success", "content": data}

            elif operation.lower() == "list":
                files = os.listdir(self.workspace)
                return {"status": "success", "files": files}

            else:
                return {"status": "error", "message": f"Unsupported operation: {operation}"}
        except Exception as e:
            logger.error("FileSystem operation failed: {}", e)
            return {"status": "error", "message": str(e)}
