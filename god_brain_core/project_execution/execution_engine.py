import asyncio
from loguru import logger
from tools.tool_registry import ToolRegistry
from agent_universe.agent_manager import AgentManager
from reality_engine.decision_core import DecisionCore
from security_omega.meta_governor import MetaGovernor
from omniversal_memory.knowledge_brain import KnowledgeBrain

# Phase 8 Personality
from existence_layer.personality_engine import PersonalityEngine

class ExecutionEngine:
    """Handles the actual execution of individual tasks."""

    def __init__(self, registry: ToolRegistry, knowledge: KnowledgeBrain, identity_core=None):
        self.registry = registry
        self.knowledge = knowledge
        self.agent_manager = AgentManager()
        self.decision_core = DecisionCore()
        self.governor = MetaGovernor()
        self.personality = PersonalityEngine(identity_core) if identity_core else None

    async def execute_task(self, task: dict):
        """Runs the cognitive cycle for a specific task."""
        task_name = task["task"]
        logger.info("ENGINE: Executing task '{}'", task_name)

        try:
            # 1. Memory context
            context_results = await self.knowledge.semantic_search(task_name, k=2)
            context = " ".join([r["text"] for r in context_results])

            # 2. Parallel Agent Proposals
            proposals = await self.agent_manager.coordinate(task_name, context)

            # 3. Phase 8: Personality Influence
            if self.personality:
                proposals = await self.personality.influence_decision_weight(proposals)

            # 4. Decision Synthesis
            decision = await self.decision_core.synthesize(task_name, proposals)

            # 5. Meta-Governor Audit
            authorized, reason = await self.governor.authorize_action(task_name, decision)
            if not authorized:
                return {"status": "blocked", "reason": reason, "decision": decision}

            # 6. Tool Execution
            tool_name = "LoggerTool"
            if "search" in task_name.lower(): tool_name = "WebSearchTool"
            elif "file" in task_name.lower(): tool_name = "FileSystemTool"
            elif "api" in task_name.lower(): tool_name = "APITool"

            tool = self.registry.get_tool(tool_name)
            if not tool: tool = self.registry.get_tool("LoggerTool")

            if tool_name == "FileSystemTool":
                outcome = await tool.execute(operation="write", filename=f"task_{task['id']}.txt", content=str(decision))
            else:
                outcome = await tool.execute(message=f"Task {task['id']} complete: {decision['refined_action'][:30]}...")

            # 7. Store result
            await self.knowledge.ingest_knowledge(f"Result for task {task['id']}: {outcome['status']}", source="execution_engine")

            return {"status": "success", "outcome": outcome, "decision": decision}

        except Exception as e:
            logger.exception("Task execution failed: {}", e)
            return {"status": "error", "message": str(e)}
        finally:
            await asyncio.sleep(0.5)
