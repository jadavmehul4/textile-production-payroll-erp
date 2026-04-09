from datetime import datetime
from typing import List, Dict, Any

class MemoryManager:
    """
    Manages short-term system memory and event logging.
    Designed for in-memory storage (max 50 entries) before transitioning to Qdrant.
    """
    def __init__(self, limit: int = 50):
        self._storage: List[Dict[str, Any]] = []
        self._limit = limit

    def add(self, entry: Dict[str, Any]):
        """
        Adds a new entry to memory. Removes oldest if limit exceeded.
        """
        entry["timestamp"] = datetime.now().isoformat()

        self._storage.append(entry)

        # Enforce storage limit
        if len(self._storage) > self._limit:
            self._storage.pop(0)

        print(f"[MemoryManager] New memory stored. Total entries: {len(self._storage)}")

    def get_recent(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves the most recent entries from memory.
        """
        return self._storage[-limit:]

# Global instance
memory_manager = MemoryManager()
