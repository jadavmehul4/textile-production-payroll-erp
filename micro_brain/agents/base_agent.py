from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    """
    Abstract base class for all autonomous agents in the system.
    """
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def execute(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the logic associated with a structured command.
        """
        pass

    def log(self, message: str):
        """
        Standard logging method for agents.
        """
        print(f"[{self.name}] {message}")
