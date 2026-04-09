from typing import Dict, Any, Optional
from micro_brain.agents.base_agent import BaseAgent
from micro_brain.agents.task_agent import TaskAgent

class AgentManager:
    """
    Orchestrates the selection and initialization of specialized agents.
    """
    def __init__(self):
        self._task_agent = TaskAgent()

    def get_agent(self, command: Dict[str, Any]) -> Optional[BaseAgent]:
        """
        Determines which agent should handle the given command.
        """
        action = command.get("action")

        if action == "generate_report":
            return self._task_agent

        return None

# Global instance
agent_manager = AgentManager()
