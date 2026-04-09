from typing import Any, Optional
from micro_brain.security.pin_auth import PinAuth
from micro_brain.security.voice_auth import VoiceAuth

class SecurityManager:
    """
    Orchestrates the multi-factor authentication (Voice + PIN).
    """
    def __init__(self):
        self.pin_auth = PinAuth()
        self.voice_auth = VoiceAuth()

    def is_authorized(
        self,
        audio_sample: Any,
        require_pin: bool = False,
        pin: Optional[str] = None
    ) -> bool:
        """
        Validates if the user is authorized based on voice and optionally a PIN.
        """
        # Step 1: Verify Voiceprint
        if not self.voice_auth.verify_speaker(audio_sample):
            print("[SecurityManager] Voice verification failed.")
            return False

        # Step 2: Verify PIN if required
        if require_pin:
            if not pin:
                print("[SecurityManager] PIN required but not provided.")
                return False
            if not self.pin_auth.verify_pin(pin):
                print("[SecurityManager] PIN verification failed.")
                return False

        return True

# Global instance
security_manager = SecurityManager()
