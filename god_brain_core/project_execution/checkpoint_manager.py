import os
import json
from loguru import logger

class CheckpointManager:
    """Saves and loads system state to ensure crash recovery."""

    def __init__(self, storage_path="/app/god_brain_core/workspace/checkpoints/"):
        self.storage_path = storage_path
        os.makedirs(self.storage_path, exist_ok=True)

    async def save_checkpoint(self, project_id: str, state: dict):
        """Persists the current state to a JSON file."""
        filename = f"checkpoint_{project_id}.json"
        path = os.path.join(self.storage_path, filename)

        try:
            with open(path, "w") as f:
                json.dump(state, f, indent=4)
            logger.info("Saved checkpoint for project: {}", project_id)
            return True
        except Exception as e:
            logger.error("Failed to save checkpoint: {}", e)
            return False

    async def load_checkpoint(self, project_id: str):
        """Retrieves the state from a JSON file."""
        filename = f"checkpoint_{project_id}.json"
        path = os.path.join(self.storage_path, filename)

        if not os.path.exists(path):
            logger.warning("No checkpoint found for project: {}", project_id)
            return None

        try:
            with open(path, "r") as f:
                state = json.load(f)
            logger.success("Loaded checkpoint for project: {}", project_id)
            return state
        except Exception as e:
            logger.error("Failed to load checkpoint: {}", e)
            return None

    async def list_checkpoints(self):
        """Lists all projects with available checkpoints."""
        files = os.listdir(self.storage_path)
        return [f.replace("checkpoint_", "").replace(".json", "") for f in files if f.startswith("checkpoint_")]
