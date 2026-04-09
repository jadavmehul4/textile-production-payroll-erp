import threading
import time
import asyncio
from typing import Any
from micro_brain.core.event_bus import event_bus
from micro_brain.voice.stt import transcribe

class VoiceListener:
    """
    Background listener for voice commands.
    Simulates wake-word detection and STT conversion.
    """
    def __init__(self):
        self._running = False
        self._thread = None
        self._loop = None

    def start(self):
        """
        Starts the listener in a background thread.
        """
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """
        Stops the listener.
        """
        self._running = False

    def _run(self):
        """
        Main loop for voice simulation.
        """
        # Create a new event loop for this thread to handle async emissions
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        print("[VoiceListener] Started background listening...")

        while self._running:
            # Simulate waiting for wake word
            time.sleep(5)

            if not self._running:
                break

            print("[VoiceListener] Wake word detected!")

            # Simulate capturing audio and transcribing
            command_text = transcribe(None)
            print(f"[VoiceListener] Captured command: {command_text}")

            # Emit event to the system
            self._loop.run_until_complete(
                event_bus.emit("voice_command", {"text": command_text})
            )

        self._loop.close()

# Global instance
voice_listener = VoiceListener()
