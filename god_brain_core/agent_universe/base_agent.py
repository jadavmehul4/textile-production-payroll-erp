from loguru import logger
import asyncio
from intelligence_amplifier.llm_brain import LLMBrain

class BaseAgent:
    """Base class for all cognitive agents."""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.llm = LLMBrain()

    async def process(self, goal: str, context: str, shared_state: dict):
        """Processes the goal from the agent's specific perspective."""
        logger.info("Agent {} ({}) processing goal...", self.name, self.role)

        # Agents use LLM to reason from their perspective
        prompt = f"As a {self.role}, analyze the following goal and provide a proposal.\nGoal: {goal}\nContext: {context}"
        proposal_text = await self.llm.reason(prompt, context=str(shared_state))

        # Mock confidence and risk for demonstration
        # In a real scenario, the LLM would output structured data
        proposal = {
            "agent": self.name,
            "role": self.role,
            "proposal": proposal_text,
            "confidence": 0.85 if "Success" in proposal_text else 0.7,
            "risk": 0.1 if "safe" in proposal_text.lower() else 0.3
        }

        return proposal
