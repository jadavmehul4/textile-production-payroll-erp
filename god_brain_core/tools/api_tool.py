import httpx
import asyncio
from loguru import logger
from tools.base_tool import BaseTool

class APITool(BaseTool):
    """Safe API integration tool for whitelisted domains with real HTTP handling."""

    def __init__(self):
        self.whitelist = ["api.openai.com", "api.github.com", "api.duckduckgo.com", "localhost"]
        super().__init__(
            name="APITool",
            description="Performs whitelisted GET/POST requests with production-grade handling."
        )

    def _is_whitelisted(self, url: str):
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        return any(domain == w or domain.endswith("." + w) for w in self.whitelist)

    async def execute(self, method: str, url: str, payload: dict = None, headers: dict = None):
        """Executes real HTTP requests if whitelisted."""
        logger.info("API request initiated: {} {}", method, url)

        if not self._is_whitelisted(url):
            logger.warning("Access Denied: Domain '{}' is not in the secure whitelist.", url)
            return {"status": "error", "message": "Domain not whitelisted"}

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=headers)
                elif method.upper() == "POST":
                    response = await client.post(url, json=payload, headers=headers)
                else:
                    return {"status": "error", "message": f"Unsupported method: {method}"}

                response.raise_for_status()
                logger.success("API request successful for {}", url)
                return {"status": "success", "url": url, "response": response.json() if 'application/json' in response.headers.get('content-type', '') else response.text}

        except Exception as e:
            logger.error("API tool failure: {}", e)
            return {"status": "error", "message": str(e)}
