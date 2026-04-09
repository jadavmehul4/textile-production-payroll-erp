from typing import Dict, Any, List

class GoalEngine:
    """
    Generates proactive autonomous goals based on detected patterns and current context.
    """
    def generate(self, learning_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates goals and recommended actions.
        """
        goals = []
        suggested_actions = []

        frequent_actions = learning_data.get("frequent_actions", [])
        time_of_day = context.get("time_of_day", "unknown")
        last_intent = context.get("last_intent")

        # 1. Generate goals from frequent actions
        for action in frequent_actions:
            if action == "open_app":
                goals.append("Optimize application usage")
                suggested_actions.append("Suggest auto-launch for frequent apps")

            elif action == "generate_report":
                goals.append("Automate report generation")
                suggested_actions.append("Schedule daily report processing")

        # 2. Context-based prioritization/additions
        if time_of_day == "morning":
            goals.insert(0, "Maximize morning productivity")
            suggested_actions.insert(0, "Prepare dashboard for daily review")

        # 3. Last intent bias (simple matching)
        if last_intent and last_intent.get("domain") == "production":
            goals.append("Monitor production efficiency")
            suggested_actions.append("Enable real-time production alerts")

        return {
            "goals": goals,
            "actions": suggested_actions
        }

# Global instance
goal_engine = GoalEngine()
