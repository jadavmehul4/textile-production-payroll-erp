import asyncio

class MemoryCore:
    def __init__(self):
        self.name = "Memory Core"

    async def store_experience(self, experience: str):
        await asyncio.sleep(0.01)
        return True

    async def recall_context(self, query: str):
        await asyncio.sleep(0.01)
        return f"Context for {query}"
