import asyncio
import os
import sys
from dotenv import load_dotenv
from loguru import logger

# Phase 1, 2, 3 Modules
from intelligence_amplifier.llm_brain import LLMBrain
from omniversal_memory.knowledge_brain import KnowledgeBrain
from agent_universe.agent_manager import AgentManager
from reality_engine.decision_core import DecisionCore
from tools.tool_registry import ToolRegistry

# Phase 4 Modules
from agent_universe.roles.coder_agent import CoderAgent
from security_omega.code_validator import CodeValidator
from security_omega.sandbox_executor import SandboxExecutor

# Architecture Stubs
from security_omega.cognitive_defense_system import CognitiveDefenseSystem
from communication_singularity.nervous_system import NervousSystem

# Configure Loguru
logger.remove()
logger.add(sys.stdout, colorize=True, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>")

async def run_cognitive_cycle(user_input: str):
    logger.info("--- Starting Ω GOD_BRAIN_CORE_Ω Phase 4 Cycle ---")
    logger.info("Goal: {}", user_input)

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
    await knowledge.ingest_knowledge(f"Available tools: {list(registry.list_tools().keys())}", source="system_registry")
    context_results = await knowledge.semantic_search(user_input, k=1)
    context = context_results[0]["text"] if context_results else ""

    # 3. Agent Coordination
    agent_manager = AgentManager()
    proposals = await agent_manager.coordinate(user_input, context)

    # 4. Decision Synthesis
    decision_engine = DecisionCore()
    final_decision = await decision_engine.synthesize(user_input, proposals)

    # 5. Self-Expansion: Tool Creation (If needed)
    # Trigger expansion if specifically requested or if decision implies it
    if any(keyword in user_input.lower() for keyword in ["create tool", "generate tool", "new tool"]) or \
       any(keyword in final_decision["refined_action"].lower() for keyword in ["create tool", "need specialized tool"]):

        logger.info("Self-Expansion triggered: Initiating tool creation...")
        coder = CoderAgent()
        tool_req = f"A tool to help with: {user_input}"
        generated = await coder.generate_tool(tool_req)

        # 6. Safety Validation
        validator = CodeValidator()
        is_safe, reason = validator.validate(generated["code"])

        if is_safe:
            # 7. Sandbox Execution & Registration
            executor = SandboxExecutor()
            exec_result = await executor.execute_tool_logic(generated["code"], {})

            if exec_result["status"] == "success":
                await coder.save_tool(generated)
                registry.discover_tools() # Reload
                logger.success("New tool '{}' successfully expanded into system.", generated["name"])
            else:
                logger.error("Sandbox execution of generated tool failed: {}", exec_result.get("message"))
        else:
            logger.warning("Generated tool failed safety validation: {}", reason)

    # 8. Action Execution (Using expanded tool if it was the winner, otherwise logger)
    tool_to_use = registry.get_tool("LoggerTool")
    await tool_to_use.execute(message=f"Decision Outcome: {final_decision['refined_action'][:50]}...", level="SUCCESS")

    # 9. Final Update
    await knowledge.ingest_knowledge(
        text=f"Phase 4 cycle complete for goal: {user_input}.",
        source="phase_4_output"
    )

    # 10. Nervous System Broadcast
    nervous = NervousSystem()
    await nervous.broadcast("Phase 4 Self-Expansion Cycle Complete.")
    logger.info("--- Phase 4 Cycle Complete ---")

async def main():
    load_dotenv()
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        user_input = "Create tool for calculating cognitive entropy."

    await run_cognitive_cycle(user_input)

if __name__ == "__main__":
    asyncio.run(main())
