import asyncio
import os
import hashlib
from loguru import logger
from project_execution.task_planner import TaskPlanner
from project_execution.checkpoint_manager import CheckpointManager
from project_execution.progress_tracker import ProgressTracker
from project_execution.debugger_engine import DebuggerEngine
from project_execution.execution_engine import ExecutionEngine
from tools.tool_registry import ToolRegistry
from omniversal_memory.knowledge_brain import KnowledgeBrain

# Phase 8 Entities
from existence_layer.identity_core import IdentityCore
from hyper_meta_cognition.self_awareness_engine import SelfAwarenessEngine
from omniversal_memory.self_memory import SelfMemory

# Phase 7 Distributed
from distributed_system.task_dispatcher import TaskDispatcher

class ProjectManager:
    """Orchestrates large-scale project autonomy with distributed execution."""

    def __init__(self, registry: ToolRegistry, knowledge: KnowledgeBrain, dispatcher: TaskDispatcher = None):
        self.registry = registry
        self.knowledge = knowledge
        self.dispatcher = dispatcher
        self.planner = TaskPlanner()
        self.checkpoint_mgr = CheckpointManager()
        self.debugger = DebuggerEngine()

        self.identity = IdentityCore()
        self.self_memory = SelfMemory(knowledge)
        self.engine = ExecutionEngine(registry, knowledge, self.identity)

    async def run_project(self, goal: str):
        """Persistent goal execution with distributed support and identity evolution."""
        project_id = hashlib.md5(goal.encode()).hexdigest()[:8]
        logger.info("--- GOAL LOCK ACTIVATED: Project {} ---", project_id)

        state = await self.checkpoint_mgr.load_checkpoint(project_id)
        if state:
            tasks = state["tasks"]
        else:
            tasks = await self.planner.generate_plan(goal)
            state = {"project_id": project_id, "goal": goal, "tasks": tasks, "completed_ids": []}
            await self.checkpoint_mgr.save_checkpoint(project_id, state)

        tracker = ProgressTracker(tasks)
        for tid in state.get("completed_ids", []):
            tracker.mark_complete(tid)

        awareness = SelfAwarenessEngine(self.identity, tracker)

        while not tracker.is_project_complete():
            if tracker.detect_stagnation():
                logger.error("Project stalled.")
                break

            awareness_report = await awareness.generate_awareness_report()
            ready_tasks = tracker.get_ready_tasks()

            if not ready_tasks: break

            for task in ready_tasks:
                logger.info("Task {}: {}", task["id"], task["task"])

                # DISTRIBUTED ROUTING (PHASE 7 INTEGRATION)
                if self.dispatcher:
                    # Distribute to network
                    success_signal = await self.dispatcher.dispatch_task(task)
                    # For demo, the local engine still handles primary execution
                    # but signals are sent over the bus.
                    result = await self.engine.execute_task(task)
                else:
                    result = await self.engine.execute_task(task)

                if result["status"] == "success":
                    tracker.mark_complete(task["id"])
                    state["completed_ids"].append(task["id"])
                    await self.checkpoint_mgr.save_checkpoint(project_id, state)
                    await self.identity.evolve_identity(result["decision"], result["outcome"])
                    await self.self_memory.record_episode(task["task"], awareness_report, "success")
                else:
                    fix = await self.debugger.debug_failure(task, result.get("message", "N/A"))
                    if fix["retry_recommended"]:
                        result = await self.engine.execute_task(task)
                        if result["status"] == "success":
                            tracker.mark_complete(task["id"])
                            state["completed_ids"].append(task["id"])
                            await self.checkpoint_mgr.save_checkpoint(project_id, state)

            await asyncio.sleep(1)

        return tracker.is_project_complete()
