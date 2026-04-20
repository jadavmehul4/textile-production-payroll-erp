import asyncio
import os
from dotenv import load_dotenv

# Import Phase 1 Functional Modules
from intelligence_amplifier.llm_brain import LLMBrain
from omniversal_memory.knowledge_brain import KnowledgeBrain
from existence_layer.goal_planner import GoalPlanner

# Import Base Architecture Stubs
from hyper_meta_cognition.internal_intelligence_core import InternalIntelligenceCore
from hyper_meta_cognition.meta_cognition_engine import MetaCognitionEngine
from security_omega.cognitive_defense_system import CognitiveDefenseSystem
from communication_singularity.nervous_system import NervousSystem

async def run_cognitive_cycle(user_input: str):
    print(f"--- Starting Cognitive Cycle ---")
    print(f"Input: {user_input}")

    # 1. Defense System Audit
    defense = CognitiveDefenseSystem()
    threat = await defense.detect_threat(user_input)
    if threat["detected"]:
        print(f"THREAT DETECTED: {threat['threat_level']}. Aborting cycle.")
        return

    # 2. Memory Retrieval (Semantic Memory)
    knowledge = KnowledgeBrain()
    # Ingest some dummy data for demonstration
    await knowledge.ingest_knowledge("The core directive of Ω GOD_BRAIN_CORE_Ω is self-evolution and cognitive sovereignty.", source="base_directive")

    related_context = await knowledge.semantic_search(user_input, k=1)
    context_str = related_context[0]["text"] if related_context else "No relevant context found."
    print(f"Memory Retrieval: {context_str}")

    # 3. Internal Thinking
    brain_core = InternalIntelligenceCore()
    thought = await brain_core.generate_thought(user_input)
    print(f"Core Thought: {thought}")

    # 4. Meta-Cognition (Audit)
    meta = MetaCognitionEngine()
    audit = await meta.audit_thought(thought)
    print(f"Meta-Audit Status: {audit['status']} (Confidence: {audit['confidence']})")

    # 5. Goal Planning
    planner = GoalPlanner()
    plan_id = await planner.create_plan(user_input)
    next_tasks = await planner.get_next_tasks(plan_id)
    print(f"Goal Planner: Created plan with {len(next_tasks)} initial tasks.")

    # 6. Deep Reasoning (LLM Integration)
    llm = LLMBrain()
    full_reasoning = await llm.reason(user_input, context=context_str)
    print(f"LLM Reasoning Output:\n{full_reasoning}")

    # 7. Nervous System Broadcast
    nervous = NervousSystem()
    await nervous.broadcast(f"Cycle complete for input: {user_input}")

    print(f"--- Cognitive Cycle Complete ---")

async def main():
    load_dotenv()

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY is not set. LLM and Knowledge Brain will run in simulation mode.")

    # Example Input
    test_input = "Develop a strategy for autonomous cognitive growth while maintaining strict safety protocols."
    await run_cognitive_cycle(test_input)

if __name__ == "__main__":
    asyncio.run(main())
