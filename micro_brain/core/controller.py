from typing import Dict, Any
from micro_brain.core.action_executor import action_executor
from micro_brain.agents.agent_manager import agent_manager

class Controller:
    """
    Abstracts device execution, providing a unified interface for the brain
    to interact with system actions and autonomous agents.
    """
    def execute(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a command by delegating to the appropriate subsystem.
        """
        action = command.get("action")

        # 1. Check for autonomous agent handling (Multi-step tasks)
        agent = agent_manager.get_agent(command)
        if agent:
            print(f"[Controller] Routing to agent: {agent.name}")
            return agent.execute(command)

        # 2. Check for direct action execution (Single system commands)
        if action == "open_app":
            print("[Controller] Routing to ActionExecutor")
            return action_executor.execute(command)

        # 3. Fallback for unsupported actions
        return {
            "status": "error",
            "message": f"Controller cannot resolve execution for action: {action}"
        }

# Global instance
controller = Controller()
