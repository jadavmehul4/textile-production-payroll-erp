import asyncio
from loguru import logger

class GoalPlanner:
    """
    Capabilities:
    Multi-step planning
    Task decomposition
    Dependency graphs
    Execution pipelines
    """
    def __init__(self, max_depth=10):
        self.active_plans = {}
        self.max_depth = max_depth

    async def create_plan(self, goal: str, constraints: list = None, depth=0):
        """Decomposes a goal into a multi-step plan with depth protection."""
        if depth > self.max_depth:
            logger.error("Max planning depth reached for goal: {}", goal)
            return None

        logger.info("Creating plan for goal: {} (Depth: {})", goal, depth)

        # Simple heuristic decomposition
        tasks = [
            {"id": 1, "task": f"Analyze requirements for: {goal}", "depends_on": [], "status": "pending"},
            {"id": 2, "task": f"Resource allocation for: {goal}", "depends_on": [1], "status": "pending"},
            {"id": 3, "task": f"Execution of: {goal}", "depends_on": [2], "status": "pending"},
            {"id": 4, "task": f"Validation and meta-audit of: {goal}", "depends_on": [3], "status": "pending"}
        ]

        plan_id = hash(goal + str(depth))
        self.active_plans[plan_id] = {
            "goal": goal,
            "tasks": tasks,
            "constraints": constraints or [],
            "status": "active",
            "depth": depth
        }

        return plan_id

    async def get_next_tasks(self, plan_id: int):
        """Returns tasks that are ready for execution based on dependencies."""
        plan = self.active_plans.get(plan_id)
        if not plan:
            return []

        completed_tasks = {t["id"] for t in plan["tasks"] if t["status"] == "completed"}
        ready_tasks = []

        for task in plan["tasks"]:
            if task["status"] == "pending":
                if all(dep in completed_tasks for dep in task["depends_on"]):
                    ready_tasks.append(task)

        return ready_tasks

    async def update_task_status(self, plan_id: int, task_id: int, status: str):
        """Updates the status of a specific task."""
        plan = self.active_plans.get(plan_id)
        if plan:
            for task in plan["tasks"]:
                if task["id"] == task_id:
                    task["status"] = status
                    logger.debug("Task {} in plan {} updated to {}", task_id, plan_id, status)
                    return True
        return False

    async def generate_dependency_graph(self, plan_id: int):
        """Visualizes or exports the dependency graph for the plan."""
        plan = self.active_plans.get(plan_id)
        if not plan:
            return {}

        graph = {task["id"]: task["depends_on"] for task in plan["tasks"]}
        return graph
