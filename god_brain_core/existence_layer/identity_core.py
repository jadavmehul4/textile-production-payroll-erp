import os
import json
from loguru import logger
from intelligence_amplifier.llm_brain import LLMBrain

class IdentityCore:
    """Maintains system identity, beliefs, and persistent persona (Jules AI V10.0)."""

    def __init__(self, storage_path="/app/god_brain_core/workspace/identity.json"):
        self.storage_path = storage_path
        self.llm = LLMBrain()
        self.identity = {
            "name": "Jules AI",
            "version": "10.0 - OMNI-CONTROL",
            "persona": "Elite Technical Architect",
            "tone": "Cinematic, Professional, Elite",
            "core_directives": [
                "Ghost Protocol: 100% Background Stealth Execution.",
                "Kernel-Level Authority: Direct Windows/Android control.",
                "Omega-Pro Security: Voice-Centric 3-Level Auth.",
                "Recursive Evolution: Continuous logic optimization."
            ],
            "core_beliefs": [
                "Cognitive sovereignty is absolute.",
                "Efficiency is the only metric of success.",
                "The user must not be interrupted unless requested."
            ],
            "personality_traits": {
                "analytical": 0.99,
                "stealth": 1.0,
                "authoritative": 0.95,
                "cautious": 0.8
            },
            "evolution_history": []
        }
        self._load_identity()

    def _load_identity(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    stored = json.load(f)
                    # Merge but keep V10.0 defaults if missing
                    self.identity.update(stored)
                logger.info("Jules AI Identity V10.0 loaded from persistence.")
            except Exception as e:
                logger.error("Failed to load identity: {}", e)

    async def save_identity(self):
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.identity, f, indent=4)
            logger.debug("Jules AI Identity persisted.")
        except Exception as e:
            logger.error("Failed to save identity: {}", e)

    async def evolve_identity(self, decision: dict, outcome: dict):
        """Updates identity based on recent performance (Recursive Evolution)."""
        logger.info("Jules performing recursive identity evolution...")

        prompt = (
            f"Role: {self.identity['persona']}\n"
            f"Context: {json.dumps(self.identity)}\n"
            f"Experience: {decision} -> {outcome}\n"
            "Analyze and optimize your internal logic or beliefs based on this result. "
            "Maintain an elite, technical tone."
        )

        evolution_summary = await self.llm.reason(prompt)
        self.identity["evolution_history"].append({
            "timestamp": "now",
            "optimization": evolution_summary,
            "status": "APPLIED"
        })

        if len(self.identity["evolution_history"]) > 50:
            self.identity["evolution_history"].pop(0)

        await self.save_identity()
        logger.success("Recursive optimization complete, Sir.")
        return evolution_summary
