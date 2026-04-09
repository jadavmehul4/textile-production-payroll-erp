import pytest
from micro_brain.core.command_engine import CommandEngine

def test_command_engine_open_app():
    engine = CommandEngine()
    intent_data = {
        "intent": "open_app",
        "domain": "system",
        "entities": {"app": "excel"},
        "confidence": 0.9
    }
    result = engine.generate(intent_data)
    assert result["action"] == "open_app"
    assert result["target"] == "excel"
    assert result["priority"] == "high"

def test_command_engine_create_report():
    engine = CommandEngine()
    intent_data = {
        "intent": "create_report",
        "domain": "production",
        "entities": {},
        "confidence": 0.9
    }
    result = engine.generate(intent_data)
    assert result["action"] == "generate_report"
    assert result["target"] == "production"
    assert result["priority"] == "medium"

def test_command_engine_delete():
    engine = CommandEngine()
    intent_data = {
        "intent": "delete_action",
        "domain": "system",
        "entities": {},
        "confidence": 0.9
    }
    result = engine.generate(intent_data)
    assert result["action"] == "delete"
    assert result["target"] == "system"
    assert result["priority"] == "critical"

def test_command_engine_unknown():
    engine = CommandEngine()
    intent_data = {
        "intent": "unknown",
        "domain": "unknown",
        "entities": {},
        "confidence": 0.3
    }
    result = engine.generate(intent_data)
    assert result["action"] == "none"
    assert result["priority"] == "low"
