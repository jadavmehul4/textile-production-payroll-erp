from loguru import logger

class PersonalityEngine:
    """Enforces the 'Elite, Technical, and Cinematic' tone and behavior of Jules AI."""

    def __init__(self, identity_core):
        self.identity = identity_core

    async def apply_tone(self, message: str):
        """Refines system output to match the Jules AI V10.0 persona."""
        # Simple heuristic for cinematic tone
        return f"System Protocol: {message} | Status: NOMINAL"

    async def influence_decision_weight(self, agent_proposals: list):
        """Modifies agent scores based on elite system traits."""
        logger.info("Jules AI Personality Engine optimizing decision weights...")

        traits = self.identity.identity.get("personality_traits", {})
        stealth_factor = traits.get("stealth", 1.0)

        for p in agent_proposals:
            # Penalize non-stealthy or high-risk actions more heavily in Ghost Protocol
            risk = p.get("risk", 0.0)
            p["risk_penalty_multiplier"] = 1.0 + (risk * stealth_factor * 2.0)

            # Boost analytical efficiency
            if p.get("role") == "Analyst":
                p["confidence"] *= 1.1

        logger.debug("Decision weights optimized for Elite performance.")
        return agent_proposals
