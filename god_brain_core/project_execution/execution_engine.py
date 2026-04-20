import asyncio
from loguru import logger
from tools.tool_registry import ToolRegistry
from agent_universe.agent_manager import AgentManager
from reality_engine.decision_core import DecisionCore
from security_omega.meta_governor import MetaGovernor
from omniversal_memory.knowledge_brain import KnowledgeBrain

class ExecutionEngine:
    """Handles the actual execution of individual tasks."""

    def __init__(self, registry: ToolRegistry, knowledge: KnowledgeBrain):
        self.registry = registry
        self.knowledge = knowledge
        self.agent_manager = AgentManager()
        self.decision_core = DecisionCore()
        self.governor = MetaGovernor()

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

            # 3. Decision Synthesis
            decision = await self.decision_core.synthesize(task_name, proposals)

            # 4. Meta-Governor Audit
            authorized, reason = await self.governor.authorize_action(task_name, decision)
            if not authorized:
                return {"status": "blocked", "reason": reason}

            # 5. Tool Execution (Demonstration selection)
            # In a real system, the decision would specify the tool.
            # Here we default to Logger or select based on task name.
            tool_name = "LoggerTool"
            if "search" in task_name.lower(): tool_name = "WebSearchTool"
            elif "file" in task_name.lower(): tool_name = "FileSystemTool"
            elif "api" in task_name.lower(): tool_name = "APITool"

            tool = self.registry.get_tool(tool_name)
            if not tool: tool = self.registry.get_tool("LoggerTool")

            # Simplified tool call for demo
            if tool_name == "FileSystemTool":
                outcome = await tool.execute(operation="write", filename=f"task_{task['id']}.txt", content=str(decision))
            else:
                outcome = await tool.execute(message=f"Task {task['id']} complete: {decision['refined_action'][:30]}...")

            # 6. Store result
            await self.knowledge.ingest_knowledge(f"Result for task {task['id']}: {outcome['status']}", source="execution_engine")

            return {"status": "success", "outcome": outcome}

        except Exception as e:
            logger.exception("Task execution failed: {}", e)
            return {"status": "error", "message": str(e)}
        finally:
            # Short rest between tasks to prevent rate limits
            await asyncio.sleep(0.5)
