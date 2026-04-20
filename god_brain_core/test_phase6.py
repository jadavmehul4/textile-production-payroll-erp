import unittest
import asyncio
import os
import shutil
from project_execution.checkpoint_manager import CheckpointManager
from project_execution.progress_tracker import ProgressTracker

class TestPhase6(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.test_path = "/app/god_brain_core/workspace/test_checkpoints/"
        self.checkpoint_mgr = CheckpointManager(storage_path=self.test_path)

    def tearDown(self):
        if os.path.exists(self.test_path):
            shutil.rmtree(self.test_path)

    def test_checkpoint_save_load(self):
        async def run_test():
            project_id = "test_p1"
            state = {"tasks": [{"id": 1}], "completed_ids": [1]}
            await self.checkpoint_mgr.save_checkpoint(project_id, state)

            loaded = await self.checkpoint_mgr.load_checkpoint(project_id)
            self.assertEqual(loaded["completed_ids"], [1])
        self.loop.run_until_complete(run_test())

    def test_progress_tracker(self):
        tasks = [
            {"id": 1, "depends_on": []},
            {"id": 2, "depends_on": [1]}
        ]
        tracker = ProgressTracker(tasks)

        # Task 1 should be ready
        ready = tracker.get_ready_tasks()
        self.assertEqual(len(ready), 1)
        self.assertEqual(ready[0]["id"], 1)

        # Mark 1 complete, 2 should become ready
        tracker.mark_complete(1)
        self.assertEqual(tracker.get_completion_percentage(), 50.0)

        ready = tracker.get_ready_tasks()
        self.assertEqual(ready[0]["id"], 2)

        tracker.mark_complete(2)
        self.assertTrue(tracker.is_project_complete())

if __name__ == "__main__":
    unittest.main()
