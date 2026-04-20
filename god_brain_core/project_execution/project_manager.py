import asyncio
import hashlib
from loguru import logger
from project_execution.task_planner import TaskPlanner
from project_execution.checkpoint_manager import CheckpointManager
from project_execution.progress_tracker import ProgressTracker
from project_execution.debugger_engine import DebuggerEngine
from project_execution.execution_engine import ExecutionEngine
from tools.tool_registry import ToolRegistry
from omniversal_memory.knowledge_brain import KnowledgeBrain

class ProjectManager:
    """Orchestrates large-scale project autonomy and Goal Lock."""

    def __init__(self, registry: ToolRegistry, knowledge: KnowledgeBrain):
        self.planner = TaskPlanner()
        self.checkpoint_mgr = CheckpointManager()
        self.debugger = DebuggerEngine()
        self.engine = ExecutionEngine(registry, knowledge)
        self.registry = registry
        self.knowledge = knowledge

    async def run_project(self, goal: str):
        """Runs a project from start to finish with crash recovery."""
        project_id = hashlib.md5(goal.encode()).hexdigest()[:8]
        logger.info("--- GOAL LOCK ACTIVATED: Project {} ---", project_id)

        # 1. Check for existing checkpoint
        state = await self.checkpoint_mgr.load_checkpoint(project_id)
        if state:
            logger.success("Resuming project from checkpoint.")
            tasks = state["tasks"]
        else:
            tasks = await self.planner.generate_plan(goal)
            state = {"project_id": project_id, "goal": goal, "tasks": tasks, "completed_ids": []}
            await self.checkpoint_mgr.save_checkpoint(project_id, state)

        tracker = ProgressTracker(tasks)
        for tid in state.get("completed_ids", []):
            tracker.mark_complete(tid)

        # 2. Continuous Execution Loop
        while not tracker.is_project_complete():
            if tracker.detect_stagnation():
                logger.error("Project stagnation. Aborting loop for safety.")
                break

            ready_tasks = tracker.get_ready_tasks()
            if not ready_tasks:
                logger.warning("No tasks ready but project not complete. Deadlock?")
                break

            for task in ready_tasks:
                logger.info("Progress: {}% | Executing Task {}: {}",
                            tracker.get_completion_percentage(), task["id"], task["task"])

                result = await self.engine.execute_task(task)

                if result["status"] == "success":
                    tracker.mark_complete(task["id"])
                    state["completed_ids"].append(task["id"])
                    await self.checkpoint_mgr.save_checkpoint(project_id, state)
                else:
                    # Trigger Debugger
                    fix_data = await self.debugger.debug_failure(task, result.get("message", "Unknown error"))
                    if fix_data["retry_recommended"]:
                        logger.info("Retrying task {} based on debugger strategy...", task["id"])
                        # Simplified retry once
                        result = await self.engine.execute_task(task)
                        if result["status"] == "success":
                            tracker.mark_complete(task["id"])
                            state["completed_ids"].append(task["id"])
                            await self.checkpoint_mgr.save_checkpoint(project_id, state)

            await asyncio.sleep(1)

        if tracker.is_project_complete():
            logger.success("--- PROJECT COMPLETE: {} ---", goal)
        else:
            logger.warning("--- PROJECT SUSPENDED: {} ---", goal)

        return tracker.is_project_complete()
