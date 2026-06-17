import httpx
import asyncio
from loguru import logger
from tools.base_tool import BaseTool

class WebSearchTool(BaseTool):
    """Production-grade web search tool using DuckDuckGo."""

    def __init__(self):
        super().__init__(
            name="WebSearchTool",
            description="Performs real-time web searches and returns structured summaries."
        )
        self.base_url = "https://api.duckduckgo.com/"

    async def execute(self, query: str):
        """Searches the web using DuckDuckGo API."""
        logger.info("Jules AI: Querying external intelligence for: {}", query)

        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()

                # Extract structured result
                abstract = data.get("AbstractText", "")
                related = data.get("RelatedTopics", [])[:3]

                summary = {
                    "abstract": abstract if abstract else "No direct abstract found.",
                    "related_references": [r.get("Text", "") for r in related if "Text" in r]
                }

                logger.success("External search complete for query: {}", query)
                return {"status": "success", "query": query, "data": summary}

        except Exception as e:
            logger.error("Web search tool failed: {}", e)
            return {"status": "error", "message": f"Failed to retrieve data: {str(e)}"}
