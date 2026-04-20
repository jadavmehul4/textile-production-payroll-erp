import asyncio
import os
import sys
from dotenv import load_dotenv
from loguru import logger

# Import Phase 1 Functional Modules
from intelligence_amplifier.llm_brain import LLMBrain
from omniversal_memory.knowledge_brain import KnowledgeBrain
from existence_layer.goal_planner import GoalPlanner

# Import Base Architecture Stubs
from hyper_meta_cognition.internal_intelligence_core import InternalIntelligenceCore
from hyper_meta_cognition.meta_cognition_engine import MetaCognitionEngine
from security_omega.cognitive_defense_system import CognitiveDefenseSystem
from communication_singularity.nervous_system import NervousSystem

# Configure Loguru
logger.remove()
logger.add(sys.stdout, colorize=True, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>")

async def run_cognitive_cycle(user_input: str):
    logger.info("--- Starting Cognitive Cycle ---")
    logger.info("User Input: {}", user_input)

    # 1. Defense System Audit
    defense = CognitiveDefenseSystem()
    threat = await defense.detect_threat(user_input)
    if threat["detected"]:
        logger.error("THREAT DETECTED: {}. Aborting cycle.", threat['threat_level'])
        return

    # 2. Memory Retrieval (Semantic Memory)
    knowledge = KnowledgeBrain()
    # Ingest some base directive for context
    await knowledge.ingest_knowledge("The core directive of Ω GOD_BRAIN_CORE_Ω is self-evolution and cognitive sovereignty.", source="base_directive")

    related_context = await knowledge.semantic_search(user_input, k=1)
    context_str = related_context[0]["text"] if related_context else "No relevant context found."
    logger.info("Memory Retrieval: {}", context_str)

    # 3. Internal Thinking
    brain_core = InternalIntelligenceCore()
    thought = await brain_core.generate_thought(user_input)
    logger.info("Core Thought: {}", thought)

    # 4. Meta-Cognition (Audit)
    meta = MetaCognitionEngine()
    audit = await meta.audit_thought(thought)
    logger.info("Meta-Audit Status: {} (Confidence: {})", audit['status'], audit['confidence'])

    # 5. Goal Planning
    planner = GoalPlanner()
    plan_id = await planner.create_plan(user_input)
    if plan_id:
        next_tasks = await planner.get_next_tasks(plan_id)
        logger.info("Goal Planner: Created plan {} with {} initial tasks.", plan_id, len(next_tasks))
    else:
        logger.error("Goal Planner failed to create plan.")

    # 6. Deep Reasoning (LLM Integration)
    llm = LLMBrain()
    full_reasoning = await llm.reason(user_input, context=context_str)
    logger.success("LLM Reasoning Output:\n{}", full_reasoning)

    # 7. Nervous System Broadcast
    nervous = NervousSystem()
    await nervous.broadcast(f"Cycle complete for input: {user_input[:20]}...")

    logger.info("--- Cognitive Cycle Complete ---")

async def main():
    load_dotenv()

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY is not set. LLM and Knowledge Brain will run in simulation mode.")

    # Dynamic Input
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        # Fallback to a default if no args provided in non-interactive environment
        user_input = "Develop a strategy for autonomous cognitive growth while maintaining strict safety protocols."

    await run_cognitive_cycle(user_input)

if __name__ == "__main__":
    asyncio.run(main())
