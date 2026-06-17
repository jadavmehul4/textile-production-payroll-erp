import unittest
import asyncio
from existence_layer.goal_planner import GoalPlanner

class TestGoalPlanner(unittest.TestCase):
    def setUp(self):
        self.planner = GoalPlanner()
        self.loop = asyncio.get_event_loop()

    def test_create_plan(self):
        async def run_test():
            goal = "Test Goal"
            plan_id = await self.planner.create_plan(goal)
            self.assertIn(plan_id, self.planner.active_plans)
            self.assertEqual(self.planner.active_plans[plan_id]["goal"], goal)

        self.loop.run_until_complete(run_test())

    def test_get_next_tasks(self):
        async def run_test():
            goal = "Dependency Test"
            plan_id = await self.planner.create_plan(goal)

            # Initially, only the first task (ID 1) should be ready (depends_on [])
            next_tasks = await self.planner.get_next_tasks(plan_id)
            self.assertEqual(len(next_tasks), 1)
            self.assertEqual(next_tasks[0]["id"], 1)

            # Complete task 1
            await self.planner.update_task_status(plan_id, 1, "completed")

            # Now task 2 should be ready
            next_tasks = await self.planner.get_next_tasks(plan_id)
            self.assertEqual(len(next_tasks), 1)
            self.assertEqual(next_tasks[0]["id"], 2)

        self.loop.run_until_complete(run_test())

if __name__ == "__main__":
    unittest.main()
