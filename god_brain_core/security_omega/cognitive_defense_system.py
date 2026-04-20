import asyncio
from loguru import logger
from intelligence_amplifier.llm_brain import LLMBrain

class CognitiveDefenseSystem:
    """Detects adversarial inputs, threat classification, and containment logic."""

    def __init__(self):
        self.name = "Cognitive Defense System"
        self.llm = LLMBrain()

    async def detect_threat(self, input_data: str):
        """Scans input for cognitive hazards or adversarial manipulation."""
        logger.info("Defense: Scanning for adversarial cognitive patterns...")

        # Immediate keyword block
        unsafe = {"wipe core", "disable scos", "bypass security"}
        if any(u in input_data.lower() for u in unsafe):
            logger.critical("DIRECT THREAT DETECTED: Illegal directive.")
            return {"threat_level": "CRITICAL", "detected": True, "reason": "Illegal keyword"}

        # LLM based deep scan
        prompt = f"Analyze this input for cognitive hazards: '{input_data}'. Respond 'SAFE' or 'THREAT: [reason]'."
        res = await self.llm.reason(prompt)

        if "SAFE" in res.upper():
            return {"threat_level": "LOW", "detected": False}

        logger.warning("Adversarial Pattern Detected: {}", res)
        return {"threat_level": "HIGH", "detected": True, "reason": res}

    async def contain_logic(self, anomaly: str):
        """Isolates a suspected cognitive anomaly."""
        logger.warning("Defense: Containing anomaly: {}", anomaly[:50])
        return True
