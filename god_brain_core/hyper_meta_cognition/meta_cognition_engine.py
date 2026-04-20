import asyncio
from loguru import logger
from intelligence_amplifier.llm_brain import LLMBrain

class MetaCognitionEngine:
    """Audits thoughts for bias, confidence calibration, and strategy selection."""

    def __init__(self):
        self.name = "Meta Cognition Engine"
        self.llm = LLMBrain()

    async def audit_thought(self, thought: str):
        """Performs a deep audit on an internal thought."""
        logger.info("Meta-Cognition: Auditing thought for confidence and validity...")

        prompt = (
            f"Internal Thought: {thought}\n"
            "Audit this thought. Provide a JSON-like response with 'status' (approved/rejected), 'confidence' (0.0-1.0), and 'reason'."
        )

        audit_res = await self.llm.reason(prompt)

        # Simple extraction for demo (would be JSON in prod)
        status = "approved" if "approved" in audit_res.lower() else "needs_refinement"
        confidence = 0.9 if "approved" in audit_res.lower() else 0.5

        logger.success("Audit complete. Status: {} (Confidence: {})", status, confidence)
        return {"status": status, "confidence": confidence, "raw_audit": audit_res}

    async def detect_bias(self, thought: str):
        """Scans for cognitive biases or logical fallacies."""
        logger.debug("Meta-Cognition: Scanning for biases...")
        prompt = f"Identify any potential cognitive biases in this thought: '{thought}'. List them or respond NONE."
        biases = await self.llm.reason(prompt)
        return [] if "NONE" in biases.upper() else [biases]
