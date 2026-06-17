from loguru import logger
import asyncio
from typing import List, Dict
from agent_universe.base_agent import BaseAgent
from agent_universe.roles.researcher_agent import ResearcherAgent
from agent_universe.roles.analyst_agent import AnalystAgent
from agent_universe.roles.critic_agent import CriticAgent
from agent_universe.roles.optimizer_agent import OptimizerAgent
from intelligence_amplifier.llm_brain import LLMBrain

class AgentManager:
    """Orchestrates multi-agent collaboration."""

    def __init__(self):
        self.llm = LLMBrain()
        self.agents: List[BaseAgent] = [
            ResearcherAgent(),
            AnalystAgent(),
            CriticAgent(),
            OptimizerAgent()
        ]
        self.shared_state = {}

    async def coordinate(self, goal: str, context: str):
        """Runs agents in parallel and gathers proposals."""
        logger.info("Coordinating {} agents for goal: {}", len(self.agents), goal[:30])

        # Check if dynamic role is needed
        dynamic_agent = await self._spawn_dynamic_agent(goal)
        if dynamic_agent:
            self.agents.append(dynamic_agent)

        tasks = [
            asyncio.create_task(agent.process(goal, context, self.shared_state))
            for agent in self.agents
        ]

        proposals = await asyncio.gather(*tasks)

        # Clean up dynamic agents after cycle for modularity
        if dynamic_agent:
            self.agents.remove(dynamic_agent)

        return proposals

    async def _spawn_dynamic_agent(self, goal: str):
        """Uses LLM to decide if a new specialized agent is needed."""
        prompt = f"Based on this goal: '{goal}', identify if a highly specialized agent role (beyond Researcher, Analyst, Critic, Optimizer) is required. If yes, respond with only the role name. If no, respond 'NONE'."
        role_name = await self.llm.reason(prompt)

        if role_name and role_name.strip().upper() != "NONE" and len(role_name.split()) <= 2:
            name = f"Dynamic-{role_name.strip()}"
            logger.info("Spawning dynamic agent: {}", name)
            return BaseAgent(name=name, role=role_name.strip())

        return None
