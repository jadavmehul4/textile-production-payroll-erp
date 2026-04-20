import asyncio
from loguru import logger
from tools.tool_registry import ToolRegistry
from agent_universe.agent_manager import AgentManager
from reality_engine.decision_core import DecisionCore
from security_omega.meta_governor import MetaGovernor
from omniversal_memory.knowledge_brain import KnowledgeBrain
from intelligence_amplifier.llm_brain import LLMBrain
from infrastructure.task_runner import TaskRunner
import json
import re

class ExecutionEngine:
    """Handles the actual execution of individual tasks with infrastructure integration."""

    def __init__(self, registry: ToolRegistry, knowledge: KnowledgeBrain, identity_core=None):
        self.registry = registry
        self.knowledge = knowledge
        self.agent_manager = AgentManager()
        self.decision_core = DecisionCore()
        self.governor = MetaGovernor()
        self.llm = LLMBrain()
        self.task_runner = TaskRunner()
        from existence_layer.personality_engine import PersonalityEngine
        self.personality = PersonalityEngine(identity_core) if identity_core else None

    async def execute_task(self, task: dict):
        """Runs the cognitive cycle and executes through the infrastructure layer."""
        task_name = task["task"]
        task_id = str(task["id"])
        logger.info("ENGINE: Processing directive '{}'...", task_name)

        try:
            # 1. Context retrieval
            context_results = await self.knowledge.semantic_search(task_name, k=2)
            context = " ".join([r["text"] for r in context_results])

            # 2. Multi-agent processing
            proposals = await self.agent_manager.coordinate(task_name, context)

            # 3. Personality calibration
            if self.personality:
                proposals = await self.personality.influence_decision_weight(proposals)

            # 4. Decision synthesis
            decision = await self.decision_core.synthesize(task_name, proposals)

            # 5. Governance audit
            authorized, reason = await self.governor.authorize_action(task_name, decision)
            if not authorized:
                return {"status": "blocked", "reason": reason, "decision": decision}

            # 6. Infrastructure-level execution
            available_tools = self.registry.list_tools()
            tool_prompt = (
                f"Task: {task_name}\n"
                f"Action: {decision['refined_action']}\n"
                f"Tools: {list(available_tools.keys())}\n"
                "Provide selection in JSON: {'tool': 'Name', 'args': {...}}."
            )

            selection_raw = await self.llm.reason(tool_prompt)
            tool_name = "LoggerTool"
            tool_args = {"message": decision["refined_action"]}

            try:
                json_match = re.search(r'\{.*\}', selection_raw, re.DOTALL)
                if json_match:
                    sel = json.loads(json_match.group(0))
                    if sel.get("tool") in available_tools:
                        tool_name = sel["tool"]
                        tool_args = sel.get("args", {})
            except Exception:
                logger.debug("Heuristic selection fallback.")

            tool_instance = self.registry.get_tool(tool_name)

            # Execute through Sandbox
            outcome = await self.task_runner.run_code_task(
                task_id=task_id,
                code="async def execute(**kwargs): return await tool.execute(**kwargs)",
                arguments=tool_args
            )

            if outcome.get("status") != "success":
                 outcome = await tool_instance.execute(**tool_args)

            # 7. Memory synchronization
            await self.knowledge.ingest_knowledge(
                f"Completed: {task_name}. Outcome: {outcome['status']}",
                source="execution_engine"
            )

            return {"status": "success", "outcome": outcome, "decision": decision}

        except Exception as e:
            logger.error("Engine failure: {}", e)
            return {"status": "error", "message": str(e)}
        finally:
            await asyncio.sleep(0.5)
