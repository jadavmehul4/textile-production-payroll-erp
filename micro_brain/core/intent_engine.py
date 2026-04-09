import re
from typing import Dict, Any

class IntentEngine:
    """
    Rule-based engine to convert text commands into structured intents.
    To be upgraded with LLM capabilities later.
    """
    def __init__(self):
        # Define rule-based patterns
        self._rules = [
            {
                "pattern": r"open\s+(excel|word|calc)",
                "intent": "open_app",
                "domain": "system",
                "entities_map": {"app": 1}
            },
            {
                "pattern": r"create\s+report",
                "intent": "create_report",
                "domain": "general",
                "entities_map": {}
            },
            {
                "pattern": r"production\s+report",
                "intent": "create_report",
                "domain": "production",
                "entities_map": {}
            },
            {
                "pattern": r"delete\s+file",
                "intent": "delete_action",
                "domain": "system",
                "entities_map": {}
            }
        ]

    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parses text and returns a structured intent.
        """
        text = text.lower().strip()

        for rule in self._rules:
            match = re.search(rule["pattern"], text)
            if match:
                entities = {}
                for key, group_idx in rule.get("entities_map", {}).items():
                    entities[key] = match.group(group_idx)

                return {
                    "intent": rule["intent"],
                    "domain": rule["domain"],
                    "entities": entities,
                    "confidence": 0.9
                }

        return {
            "intent": "unknown",
            "domain": "unknown",
            "entities": {},
            "confidence": 0.3
        }

# Global instance
intent_engine = IntentEngine()
