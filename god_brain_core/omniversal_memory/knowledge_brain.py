import os
import numpy as np
import faiss
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

class KnowledgeBrain:
    """
    Capabilities:
    Vector embeddings
    Semantic search
    External knowledge ingestion
    Memory fusion
    """
    def __init__(self, dimension=1536):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata = []
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=self.api_key, timeout=20.0) if self.api_key else None

    async def _get_embedding(self, text: str):
        if not self.client:
            logger.debug("Generating mock embedding for: {}", text[:30])
            rng = np.random.default_rng(seed=hash(text) % (2**32))
            return rng.random(self.dimension).astype('float32')

        try:
            response = await asyncio.wait_for(
                self.client.embeddings.create(
                    input=[text.replace("\n", " ")],
                    model="text-embedding-3-small"
                ),
                timeout=15.0
            )
            return np.array(response.data[0].embedding).astype('float32')
        except Exception as e:
            logger.warning("Failed to get OpenAI embedding, falling back to mock: {}", e)
            rng = np.random.default_rng(seed=hash(text) % (2**32))
            return rng.random(self.dimension).astype('float32')

    async def ingest_knowledge(self, text: str, source: str = "unknown"):
        """Embeds and stores knowledge."""
        try:
            embedding = await self._get_embedding(text)
            embedding = embedding.reshape(1, -1)
            self.index.add(embedding)
            self.metadata.append({"text": text, "source": source})
            logger.success("Ingested knowledge from {}: {}...", source, text[:50])
            return True
        except Exception as e:
            logger.error("Failed to ingest knowledge: {}", e)
            return False

    async def semantic_search(self, query: str, k: int = 3):
        """Searches for relevant knowledge using vector similarity."""
        if self.index.ntotal == 0:
            logger.warning("Semantic search requested on empty index.")
            return []

        try:
            query_embedding = await self._get_embedding(query)
            query_embedding = query_embedding.reshape(1, -1)

            search_k = min(k, self.index.ntotal)
            distances, indices = self.index.search(query_embedding, search_k)

            results = []
            for idx in indices[0]:
                if idx != -1 and idx < len(self.metadata):
                    results.append(self.metadata[idx])

            logger.info("Semantic search found {} results for query: {}", len(results), query[:30])
            return results
        except Exception as e:
            logger.exception("Semantic search failed: {}", e)
            return []

    async def fuse_memory(self, experiences: list):
        """Fuses multiple experiences into a consolidated knowledge base."""
        count = 0
        for exp in experiences:
            if await self.ingest_knowledge(exp, source="memory_fusion"):
                count += 1
        logger.info("Fused {} memories into KnowledgeBrain", count)
        return count
