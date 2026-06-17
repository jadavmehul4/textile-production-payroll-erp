from loguru import logger

class ProgressTracker:
    """Monitors task completion and detects stagnation."""

    def __init__(self, tasks: list):
        self.tasks = tasks
        self.completed_ids = set()
        self.stagnation_counter = 0
        self.last_completed_count = 0

    def mark_complete(self, task_id: int):
        """Records a task as finished."""
        self.completed_ids.add(task_id)
        logger.debug("Task {} marked complete. Total progress: {}%", task_id, self.get_completion_percentage())

    def get_completion_percentage(self):
        """Returns the percentage of project completion."""
        if not self.tasks:
            return 100.0
        return round((len(self.completed_ids) / len(self.tasks)) * 100, 2)

    def is_project_complete(self):
        """Checks if all tasks are finished."""
        return len(self.completed_ids) >= len(self.tasks)

    def detect_stagnation(self):
        """Heuristic to check if progress has stalled."""
        current_count = len(self.completed_ids)
        if current_count == self.last_completed_count:
            self.stagnation_counter += 1
        else:
            self.stagnation_counter = 0
            self.last_completed_count = current_count

        if self.stagnation_counter > 3:
            logger.warning("STAGNATION DETECTED: No progress in {} cycles.", self.stagnation_counter)
            return True
        return False

    def get_ready_tasks(self):
        """Returns tasks whose dependencies are met."""
        ready = []
        for task in self.tasks:
            if task["id"] not in self.completed_ids:
                if all(dep in self.completed_ids for dep in task.get("depends_on", [])):
                    ready.append(task)
        return ready
