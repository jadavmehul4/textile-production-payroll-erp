from loguru import logger

class MetaGovernor:
    """Enforces risk thresholds and controls tool execution."""

    def __init__(self, risk_threshold=0.5):
        self.risk_threshold = risk_threshold
        self.unsafe_keywords = {"delete", "remove", "format", "wipe", "shutdown", "kill"}

    async def authorize_action(self, goal: str, decision: dict):
        """Analyzes a decision and determines if it's safe to execute."""
        logger.info("MetaGovernor auditing action for decision origin: {}", decision.get("agent_origin"))

        # 1. Check Risk Score
        risk = decision.get("risk", 0.0) # Using top level risk from decision synthesis

        if risk > self.risk_threshold:
            logger.error("Action DENIED: Risk score {} exceeds threshold {}", risk, self.risk_threshold)
            return False, f"Risk too high: {risk}"

        # 2. Check for Unsafe Keywords in GOAL (Input)
        for kw in self.unsafe_keywords:
            if kw in goal.lower():
                logger.error("Action DENIED: Detected unsafe keyword '{}' in goal", kw)
                return False, f"Unsafe keyword detected in goal: {kw}"

        # 3. Check for Unsafe Keywords in refined action
        action_text = decision.get("refined_action", "").lower()
        for kw in self.unsafe_keywords:
            if kw in action_text:
                logger.error("Action DENIED: Detected unsafe keyword '{}' in action", kw)
                return False, f"Unsafe keyword detected in action: {kw}"

        logger.success("Action AUTHORIZED by MetaGovernor.")
        return True, "Success"
