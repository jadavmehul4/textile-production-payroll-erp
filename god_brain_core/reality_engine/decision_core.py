from loguru import logger
from typing import List, Dict
from intelligence_amplifier.llm_brain import LLMBrain

class DecisionCore:
    """Final decision synthesis and risk/reward balancing."""

    def __init__(self):
        self.llm = LLMBrain()

    async def synthesize(self, goal: str, proposals: List[Dict]):
        """Aggregates proposals and selects the optimal path."""
        logger.info("Synthesizing final decision from {} proposals", len(proposals))

        scored_proposals = []
        for p in proposals:
            # Score = (confidence * 0.6) - (risk * 0.4)
            score = (p["confidence"] * 0.6) - (p["risk"] * 0.4)
            p["score"] = round(score, 3)
            scored_proposals.append(p)
            logger.debug("Agent {}: Score {}", p["agent"], p["score"])

        # Sort by score descending
        scored_proposals.sort(key=lambda x: x["score"], reverse=True)
        winner = scored_proposals[0]

        logger.info("Highest scored proposal by agent: {}", winner["agent"])

        # Final LLM Refinement
        refinement_prompt = (
            f"As the final evaluator, refine the following winning proposal for the goal: '{goal}'.\n"
            f"Proposed Path: {winner['proposal']}\n"
            f"Refine it for maximum efficiency and alignment with safety protocols."
        )

        refined_decision = await self.llm.reason(refinement_prompt)

        final_action = {
            "agent_origin": winner["agent"],
            "score": winner["score"],
            "original_proposal": winner["proposal"],
            "refined_action": refined_decision
        }

        return final_action
