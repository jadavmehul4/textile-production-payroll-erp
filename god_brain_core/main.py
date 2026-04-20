import asyncio
import os
import sys
from dotenv import load_dotenv
from loguru import logger

# Phase 1-4 Modules
from intelligence_amplifier.llm_brain import LLMBrain
from omniversal_memory.knowledge_brain import KnowledgeBrain
from agent_universe.agent_manager import AgentManager
from reality_engine.decision_core import DecisionCore
from tools.tool_registry import ToolRegistry
from agent_universe.roles.coder_agent import CoderAgent
from security_omega.code_validator import CodeValidator
from security_omega.sandbox_executor import SandboxExecutor
from hyper_meta_cognition.self_reflection_engine import SelfReflectionEngine
from intelligence_amplifier.self_improvement_engine import SelfImprovementEngine
from intelligence_amplifier.skill_learning_engine import SkillLearningEngine
from omniversal_memory.memory_evolution_engine import MemoryEvolutionEngine

# Phase 5 Modules
from adaptive_reality_interface.world_state import WorldState
from security_omega.meta_governor import MetaGovernor

# Architecture Stubs
from security_omega.cognitive_defense_system import CognitiveDefenseSystem
from communication_singularity.nervous_system import NervousSystem

# Configure Loguru
logger.remove()
logger.add(sys.stdout, colorize=True, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>")

async def run_cognitive_cycle(user_input: str):
    logger.info("--- Starting Ω GOD_BRAIN_CORE_Ω Phase 5 Cycle ---")

    # 0. World State Awareness
    world = WorldState()
    current_state = await world.get_state()
    logger.info("World Awareness: Uptime {}s, Status {}", round(current_state['uptime_seconds'], 2), current_state['status'])

    # 1. Defense Audit
    defense = CognitiveDefenseSystem()
    threat = await defense.detect_threat(user_input)
    if threat["detected"]:
        logger.error("THREAT DETECTED. Aborting cycle.")
        return

    # 2. Tool Discovery & Knowledge Retrieval
    registry = ToolRegistry()
    registry.discover_tools()

    knowledge = KnowledgeBrain()
    context_results = await knowledge.semantic_search(user_input, k=1)
    context = context_results[0]["text"] if context_results else ""

    # 3. Agent Coordination
    agent_manager = AgentManager()
    proposals = await agent_manager.coordinate(user_input, context)

    # 4. Decision Synthesis
    decision_engine = DecisionCore()
    final_decision = await decision_engine.synthesize(user_input, proposals)

    # 5. Meta-Governor (Phase 5 Security)
    governor = MetaGovernor()
    authorized, reason = await governor.authorize_action(user_input, final_decision)

    if not authorized:
        logger.warning("Action BLOCKED by MetaGovernor: {}", reason)
        return

    # 6. Action Execution (Phase 5 World Integration)
    # Demonstration of multiple tool types based on input
    if "search" in user_input.lower():
        tool = registry.get_tool("WebSearchTool")
        result = await tool.execute(query=user_input)
    elif "file" in user_input.lower():
        tool = registry.get_tool("FileSystemTool")
        result = await tool.execute(operation="write", filename="cycle_log.txt", content=f"Cycle at {current_state['system_time']}")
    elif "api" in user_input.lower():
        tool = registry.get_tool("APITool")
        result = await tool.execute(method="GET", url="https://api.github.com/zen")
    else:
        tool = registry.get_tool("LoggerTool")
        result = await tool.execute(message=f"Success: {final_decision['refined_action'][:50]}", level="SUCCESS")

    # 7. Reflection, Improvement, Evolution, Skill Learning
    reflection_engine = SelfReflectionEngine()
    reflection = await reflection_engine.reflect(user_input, final_decision, result)

    improvement_engine = SelfImprovementEngine()
    await improvement_engine.apply_improvement(reflection)

    skill_engine = SkillLearningEngine()
    new_skill = await skill_engine.learn_skill(context=str(reflection))

    evolution_engine = MemoryEvolutionEngine(knowledge)
    await evolution_engine.evolve_memory()

    # 8. Final Update & Broadcast
    await knowledge.ingest_knowledge(f"Goal: {user_input}. Outcome: {result['status']}. New Skill: {new_skill['skill'][:20]}", source="phase_5_completion")
    nervous = NervousSystem()
    await nervous.broadcast("Phase 5 Cycle Complete.")
    logger.info("--- Phase 5 Cycle Complete ---")

async def main():
    load_dotenv()
    user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "search for recent AI trends"
    await run_cognitive_cycle(user_input)

if __name__ == "__main__":
    asyncio.run(main())
