import asyncio
import os
import sys
from dotenv import load_dotenv
from loguru import logger

# Phase 1 Modules
from intelligence_amplifier.llm_brain import LLMBrain
from omniversal_memory.knowledge_brain import KnowledgeBrain
from existence_layer.goal_planner import GoalPlanner

# Phase 2 Modules
from agent_universe.agent_manager import AgentManager
from reality_engine.decision_core import DecisionCore
from tools.logger_tool import LoggerTool

# Architecture Stubs
from security_omega.cognitive_defense_system import CognitiveDefenseSystem
from communication_singularity.nervous_system import NervousSystem

# Configure Loguru
logger.remove()
logger.add(sys.stdout, colorize=True, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>")

async def run_cognitive_cycle(user_input: str):
    logger.info("--- Starting Ω GOD_BRAIN_CORE_Ω Phase 2 Cycle ---")
    logger.info("Goal: {}", user_input)

    # 1. Defense Audit
    defense = CognitiveDefenseSystem()
    threat = await defense.detect_threat(user_input)
    if threat["detected"]:
        logger.error("THREAT DETECTED. Aborting cycle.")
        return

    # 2. Knowledge Retrieval
    knowledge = KnowledgeBrain()
    await knowledge.ingest_knowledge("The core directive is cognitive sovereignty.", source="base")
    context_results = await knowledge.semantic_search(user_input, k=1)
    context = context_results[0]["text"] if context_results else ""

    # 3. Agent Coordination (Parallel Thinking)
    agent_manager = AgentManager()
    proposals = await agent_manager.coordinate(user_input, context)

    # 4. Decision Synthesis
    decision_engine = DecisionCore()
    final_action = await decision_engine.synthesize(user_input, proposals)
    logger.success("Final Decision Synthesized: {}", final_action["refined_action"][:100])

    # 5. Action Execution (Tools)
    tool = LoggerTool()
    await tool.execute(message=f"Executing decision from {final_action['agent_origin']}: {final_action['refined_action'][:100]}...", level="SUCCESS")

    # 6. Memory Update
    await knowledge.ingest_knowledge(
        text=f"Completed goal: {user_input}. Decision: {final_action['refined_action']}",
        source="cognitive_cycle_output"
    )

    # 7. Nervous System Broadcast
    nervous = NervousSystem()
    await nervous.broadcast("Phase 2 Cognitive Cycle Complete.")
    logger.info("--- Phase 2 Cycle Complete ---")

async def main():
    load_dotenv()
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        user_input = "Coordinate an autonomous intelligence expansion protocol."

    await run_cognitive_cycle(user_input)

if __name__ == "__main__":
    asyncio.run(main())
