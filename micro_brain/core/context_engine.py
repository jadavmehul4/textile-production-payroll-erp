from datetime import datetime
from typing import Dict, Any

class ContextEngine:
    """
    Provides situational awareness by analyzing recent activity and system state.
    """
    def build(self, memory_manager) -> Dict[str, Any]:
        """
        Builds a context object based on memory and current state.
        """
        now = datetime.now()
        hour = now.hour

        # Determine time of day
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 21:
            time_of_day = "evening"
        else:
            time_of_day = "night"

        # Get recent activity from memory
        recent_memories = memory_manager.get_recent(limit=5)

        recent_actions = [m["command"]["action"] for m in recent_memories if "command" in m]
        last_intent = recent_memories[-1]["intent"] if recent_memories else None

        return {
            "time_of_day": time_of_day,
            "recent_actions": recent_actions,
            "last_intent": last_intent,
            "timestamp": now.isoformat()
        }

# Global instance
context_engine = ContextEngine()
