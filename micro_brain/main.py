from contextlib import asynccontextmanager
from fastapi import FastAPI
from micro_brain.core.event_bus import event_bus
from micro_brain.voice.voice_listener import voice_listener
from micro_brain.security.security_manager import security_manager
from micro_brain.core.intent_engine import intent_engine

async def handle_voice_command(data: dict):
    """
    Handle incoming voice commands with security verification and intent parsing.
    """
    text = data.get("text", "").lower()
    print(f"[Main] Event Received: voice_command -> {text}")

    # Parse intent
    intent_data = intent_engine.parse(text)
    print(f"[Main] INTENT: {intent_data}")

    # Determine security requirements
    # We now use the parsed intent to determine if PIN is required
    sensitive_intents = ["delete_action", "transfer_funds"] # Example intents
    require_pin = intent_data["intent"] in sensitive_intents or any(keyword in text for keyword in ["transfer"])

    # Mock PIN for simulation if required
    mock_pin = "1234" if require_pin else None

    # Verify authorization
    authorized = security_manager.is_authorized(
        audio_sample=None,  # Placeholder for real audio data
        require_pin=require_pin,
        pin=mock_pin
    )

    if authorized:
        print(f"[Main] STATUS: AUTHORIZED for command: {text}")
        # Next Step: Forward to Agent System (later)
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
