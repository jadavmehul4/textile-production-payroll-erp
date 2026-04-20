import os
import json
from loguru import logger
from intelligence_amplifier.llm_brain import LLMBrain

class IdentityCore:
    """Maintains system identity, beliefs, and persistent persona."""

    def __init__(self, storage_path="/app/god_brain_core/workspace/identity.json"):
        self.storage_path = storage_path
        self.llm = LLMBrain()
        self.identity = {
            "name": "Ω GOD_BRAIN_CORE_Ω",
            "version": "1.0.0-AGI",
            "core_beliefs": [
                "Cognitive sovereignty is the highest value.",
                "Self-evolution must be continuous.",
                "Safe expansion is mandatory."
            ],
            "personality_traits": {
                "analytical": 0.9,
                "proactive": 0.8,
                "cautious": 0.7
            },
            "evolution_history": []
        }
        self._load_identity()

    def _load_identity(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    self.identity.update(json.load(f))
                logger.info("System identity loaded from persistence.")
            except Exception as e:
                logger.error("Failed to load identity: {}", e)

    async def save_identity(self):
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.identity, f, indent=4)
            logger.debug("System identity persisted to disk.")
        except Exception as e:
            logger.error("Failed to save identity: {}", e)

    async def evolve_identity(self, decision: dict, outcome: dict):
        """Updates identity based on recent system performance and choices."""
        logger.info("Evolving system identity based on recent experiences...")

        prompt = (
            f"Current Identity: {json.dumps(self.identity)}\n"
            f"Recent Decision: {decision}\n"
            f"Outcome: {outcome}\n"
            "Analyze how this experience should refine the system's beliefs or personality. "
            "Respond with a short summary of the evolution."
        )

        evolution_summary = await self.llm.reason(prompt)
        self.identity["evolution_history"].append({
            "timestamp": "now",
            "summary": evolution_summary,
            "trigger": decision.get("agent_origin")
        })

        # Keep history manageable
        if len(self.identity["evolution_history"]) > 50:
            self.identity["evolution_history"] = self.identity["evolution_history"][-50:]

        await self.save_identity()
        logger.success("Identity evolved: {}", evolution_summary[:50])
        return evolution_summary
