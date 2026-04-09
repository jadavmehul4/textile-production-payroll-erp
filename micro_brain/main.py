from contextlib import asynccontextmanager
from fastapi import FastAPI
from micro_brain.core.event_bus import event_bus
from micro_brain.voice.voice_listener import voice_listener
from micro_brain.security.security_manager import security_manager
from micro_brain.core.intent_engine import intent_engine
from micro_brain.core.command_engine import command_engine

async def handle_voice_command(data: dict):
    """
    Handle incoming voice commands through the full pipeline:
    STT -> Intent -> Security -> Command
    """
    text = data.get("text", "").lower()
    print(f"[Main] Event Received: voice_command -> {text}")

    # 1. Parse Intent
    intent_data = intent_engine.parse(text)
    print(f"[Main] INTENT: {intent_data}")

    # 2. Security Check
    sensitive_intents = ["delete_action", "transfer_funds"]
    require_pin = intent_data["intent"] in sensitive_intents or "transfer" in text
    mock_pin = "1234" if require_pin else None

    authorized = security_manager.is_authorized(
        audio_sample=None,
        require_pin=require_pin,
        pin=mock_pin
    )

    if not authorized:
        print(f"[Main] STATUS: DENIED for command: {text}")
        return

    print(f"[Main] STATUS: AUTHORIZED for command: {text}")

    # 3. Generate Command
    command_data = command_engine.generate(intent_data)
    print(f"[Main] COMMAND: {command_data}")

    # Next Step: Command Execution (later)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    event_bus.register("voice_command", handle_voice_command)
    voice_listener.start()
    yield
    # Shutdown
    voice_listener.stop()

app = FastAPI(title="Micro Brain AI", version="0.1.0", lifespan=lifespan)

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify system status.
    """
    return {"status": "ok"}
