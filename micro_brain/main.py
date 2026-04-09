from contextlib import asynccontextmanager
from fastapi import FastAPI
from micro_brain.core.event_bus import event_bus
from micro_brain.voice.voice_listener import voice_listener
from micro_brain.security.security_manager import security_manager

async def handle_voice_command(data: dict):
    """
    Handle incoming voice commands with security verification.
    """
    text = data.get("text", "").lower()
    print(f"[Main] Event Received: voice_command -> {text}")

    # Determine security requirements
    require_pin = any(keyword in text for keyword in ["delete", "transfer"])

    # Mock PIN for simulation if required (in production, this would be captured separately)
    mock_pin = "1234" if require_pin else None

    # Verify authorization
    authorized = security_manager.is_authorized(
        audio_sample=None,  # Placeholder for real audio data
        require_pin=require_pin,
        pin=mock_pin
    )

    if authorized:
        print(f"[Main] STATUS: AUTHORIZED for command: {text}")
    else:
        print(f"[Main] STATUS: DENIED for command: {text}")

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
