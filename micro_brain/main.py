from contextlib import asynccontextmanager
from fastapi import FastAPI
from micro_brain.core.event_bus import event_bus
from micro_brain.voice.voice_listener import voice_listener

async def handle_voice_command(data: dict):
    """
    Handle incoming voice commands.
    """
    text = data.get("text")
    print(f"[Main] Event Received: voice_command -> {text}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Register handlers and start background services
    event_bus.register("voice_command", handle_voice_command)
    voice_listener.start()
    yield
    # Shutdown: Stop background services
    voice_listener.stop()

app = FastAPI(title="Micro Brain AI", version="0.1.0", lifespan=lifespan)

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify system status.
    """
    return {"status": "ok"}

# Router inclusion placeholder
# app.include_router(api_router, prefix="/api/v1")
