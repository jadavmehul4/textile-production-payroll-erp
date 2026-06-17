from agent_universe.base_agent import BaseAgent

class CriticAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Critic-01", role="Critic")
