from loguru import logger

class PersonalityEngine:
    """Adjusts decision-making style and behavior based on identity and history."""

    def __init__(self, identity_core):
        self.identity = identity_core

    async def influence_decision_weight(self, agent_proposals: list):
        """Modifies agent scores based on the system's current personality traits."""
        logger.info("Personality Engine influencing agent selection...")

        traits = self.identity.identity.get("personality_traits", {})

        # Logic: If 'cautious' is high, penalize risk more heavily
        cautious_factor = traits.get("cautious", 0.5)

        for p in agent_proposals:
            if "risk" in p:
                # Personality-adjusted penalty: risk * (standard_weight + cautious_multiplier)
                # DecisionCore uses 0.4 standard. We add influence here.
                p["risk_penalty_multiplier"] = 1.0 + (cautious_factor * 0.5)

        logger.debug("Applied personality-driven risk weights to {} proposals.", len(agent_proposals))
        return agent_proposals
