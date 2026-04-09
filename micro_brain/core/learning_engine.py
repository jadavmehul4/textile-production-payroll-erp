from collections import Counter
from typing import Dict, Any, List

class LearningEngine:
    """
    Analyzes system history to detect patterns and suggest optimizations.
    Initial implementation uses basic frequency analysis.
    """
    def analyze(self, memory_manager) -> Dict[str, Any]:
        """
        Analyzes memory for frequent actions and patterns.
        """
        # Get last 20 entries
        memories = memory_manager.get_recent(limit=20)

        # Count actions
        actions = [m["command"]["action"] for m in memories if "command" in m]
        counts = Counter(actions)

        frequent_actions = []
        suggestions = []

        for action, count in counts.items():
            # Threshold: 3 or more occurrences
            if count >= 3:
                frequent_actions.append(action)
                suggestions.append(self._generate_suggestion(action))

        return {
            "frequent_actions": frequent_actions,
            "suggestions": suggestions
        }

    def _generate_suggestion(self, action: str) -> str:
        """
        Generates human-readable suggestions based on patterns.
        """
        suggestions_map = {
            "open_app": "You frequently open this application. Would you like me to automate this on startup?",
            "generate_report": "You generate this report often. Should I schedule it for you automatically?",
            "delete": "Frequent deletions detected. Would you like me to manage a backup of these files?"
        }

        return suggestions_map.get(
            action,
            f"Action '{action}' detected as a frequent pattern. Optimization recommended."
        )

# Global instance
learning_engine = LearningEngine()
