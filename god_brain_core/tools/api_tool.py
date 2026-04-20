import httpx
import asyncio
from loguru import logger
from tools.base_tool import BaseTool

class APITool(BaseTool):
    """Safe API integration tool for whitelisted domains."""

    def __init__(self):
        self.whitelist = ["api.openai.com", "api.github.com", "localhost"]
        super().__init__(
            name="APITool",
            description="Performs whitelisted GET/POST requests with JSON-only responses."
        )

    def _is_whitelisted(self, url: str):
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        return any(domain == w or domain.endswith("." + w) for w in self.whitelist)

    async def execute(self, method: str, url: str, payload: dict = None):
        """Executes HTTP requests if whitelisted."""
        logger.info("API Request: {} {}", method, url)

        if not self._is_whitelisted(url):
            logger.warning("API Request REJECTED: Domain not in whitelist: {}", url)
            return {"status": "error", "message": "Domain not whitelisted"}

        # Simulate API call
        await asyncio.sleep(0.3)
        logger.success("API Request successful (Simulated)")
        return {"status": "success", "url": url, "response": {"data": "whitelisted response"}}
