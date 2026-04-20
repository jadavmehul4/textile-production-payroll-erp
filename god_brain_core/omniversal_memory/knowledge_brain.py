import os
import numpy as np
import faiss
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

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
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None

    async def _get_embedding(self, text: str):
        if not self.client:
            # Mock embedding for demonstration if no API key
            rng = np.random.default_rng(seed=hash(text) % (2**32))
            return rng.random(self.dimension).astype('float32')

        try:
            response = await self.client.embeddings.create(
                input=[text.replace("\n", " ")],
                model="text-embedding-3-small"
            )
            return np.array(response.data[0].embedding).astype('float32')
        except Exception as e:
            print(f"Error getting embedding: {e}")
            rng = np.random.default_rng(seed=hash(text) % (2**32))
            return rng.random(self.dimension).astype('float32')

    async def ingest_knowledge(self, text: str, source: str = "unknown"):
        """Embeds and stores knowledge."""
        embedding = await self._get_embedding(text)
        embedding = embedding.reshape(1, -1)
        self.index.add(embedding)
        self.metadata.append({"text": text, "source": source})
        return True

    async def semantic_search(self, query: str, k: int = 3):
        """Searches for relevant knowledge using vector similarity."""
        if self.index.ntotal == 0:
            return []

        query_embedding = await self._get_embedding(query)
        query_embedding = query_embedding.reshape(1, -1)

        distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))

        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.metadata):
                results.append(self.metadata[idx])

        return results

    async def fuse_memory(self, experiences: list):
        """Fuses multiple experiences into a consolidated knowledge base."""
        for exp in experiences:
            await self.ingest_knowledge(exp, source="memory_fusion")
        return len(experiences)
