from typing import Dict, Any

class CommandEngine:
    """
    Translates structured intents into executable command definitions.
    This acts as the final mapping layer before system execution.
    """
    def generate(self, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a command based on intent data.
        """
        intent = intent_data.get("intent", "unknown")
        domain = intent_data.get("domain", "unknown")
        entities = intent_data.get("entities", {})

        if intent == "open_app":
            return {
                "action": "open_app",
                "target": entities.get("app", "unknown"),
                "parameters": {},
                "priority": "high"
            }

        elif intent == "create_report":
            return {
                "action": "generate_report",
                "target": domain,
                "parameters": {},
                "priority": "medium"
            }

        elif intent == "delete_action":
            return {
                "action": "delete",
                "target": "system",
                "parameters": {},
                "priority": "critical"
            }

        return {
            "action": "none",
            "target": "none",
            "parameters": {},
            "priority": "low"
        }

# Global instance
command_engine = CommandEngine()
