import asyncio

class NervousSystem:
    def __init__(self):
        self.name = "Nervous System"

    async def broadcast(self, message: str):
        await asyncio.sleep(0.01)
        return True

    async def heartbeat(self):
        await asyncio.sleep(0.01)
        return "OK"
