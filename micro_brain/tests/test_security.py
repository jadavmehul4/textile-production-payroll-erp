import pytest
from micro_brain.security.pin_auth import PinAuth
from micro_brain.security.voice_auth import VoiceAuth
from micro_brain.security.security_manager import SecurityManager

def test_pin_auth_verification():
    auth = PinAuth()
    # Default is 1234
    assert auth.verify_pin("1234") is True
    assert auth.verify_pin("0000") is False

def test_pin_auth_set_pin():
    auth = PinAuth()
    auth.set_pin("5678")
    assert auth.verify_pin("5678") is True
    assert auth.verify_pin("1234") is False

def test_voice_auth_placeholder():
    auth = VoiceAuth()
    assert auth.verify_speaker(None) is True

def test_security_manager_logic():
    sm = SecurityManager()
    # No PIN required
    assert sm.is_authorized(audio_sample=None, require_pin=False) is True
    # PIN required, correct PIN
    assert sm.is_authorized(audio_sample=None, require_pin=True, pin="1234") is True
    # PIN required, wrong PIN
    assert sm.is_authorized(audio_sample=None, require_pin=True, pin="9999") is False
    # PIN required, missing PIN
    assert sm.is_authorized(audio_sample=None, require_pin=True, pin=None) is False
