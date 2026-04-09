import os
import platform
import subprocess
from typing import Dict, Any

class ActionExecutor:
    """
    Executes system-level commands derived from user intents.
    Focuses on safe, non-destructive operations.
    """
    def execute(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a structured command.
        """
        action = command.get("action")
        target = command.get("target")
        priority = command.get("priority")

        # Security check: Block critical actions for now
        if priority == "critical" or action == "delete":
            return {
                "status": "error",
                "message": f"Action '{action}' is blocked for security reasons."
            }

        try:
            if action == "open_app":
                return self._open_app(target)

            elif action == "generate_report":
                return {
                    "status": "success",
                    "message": f"Report for '{target}' has been generated successfully."
                }

            return {
                "status": "error",
                "message": f"Unsupported action: {action}"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Execution failed: {str(e)}"
            }

    def _open_app(self, target: str) -> Dict[str, Any]:
        """
        Handles opening system applications.
        Supports Windows and Linux (mocked/best-effort).
        """
        system = platform.system()

        # Define application mappings
        apps = {
            "excel": {"win": "excel", "linux": "libreoffice --calc"},
            "notepad": {"win": "notepad", "linux": "gedit"}
        }

        if target not in apps:
            return {
                "status": "error",
                "message": f"Application '{target}' not recognized."
            }

        try:
            if system == "Windows":
                # Using start command for Windows
                subprocess.Popen(["start", apps[target]["win"]], shell=True)
            elif system == "Linux":
                # Best effort for Linux dev environments
                cmd = apps[target]["linux"].split()
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                return {
                    "status": "error",
                    "message": f"Operating system {system} not supported for app execution."
                }

            return {
                "status": "success",
                "message": f"Opening {target}..."
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to open {target}: {str(e)}"
            }

# Global instance
action_executor = ActionExecutor()
