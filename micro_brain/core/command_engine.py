from typing import Dict, Any, Optional

class CommandEngine:
    """
    Translates structured intents into executable command definitions.
    This acts as the final mapping layer before system execution.
    Now includes context-awareness.
    """
    def generate(self, intent_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generates a command based on intent data and situational context.
        """
        intent = intent_data.get("intent", "unknown")
        domain = intent_data.get("domain", "unknown")
        entities = intent_data.get("entities", {})

        # Context-aware logic can be added here
        # Example: If it is night, maybe lower priority for non-critical tasks?

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
