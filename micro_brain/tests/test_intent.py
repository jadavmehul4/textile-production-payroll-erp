import pytest
from micro_brain.core.intent_engine import IntentEngine

def test_intent_engine_open_app():
    engine = IntentEngine()
    result = engine.parse("open excel")
    assert result["intent"] == "open_app"
    assert result["domain"] == "system"
    assert result["entities"] == {"app": "excel"}
    assert result["confidence"] == 0.9

def test_intent_engine_create_report():
    engine = IntentEngine()
    result = engine.parse("create report")
    assert result["intent"] == "create_report"
    assert result["domain"] == "general"
    assert result["confidence"] == 0.9

def test_intent_engine_production_report():
    engine = IntentEngine()
    result = engine.parse("production report")
    assert result["intent"] == "create_report"
    assert result["domain"] == "production"
    assert result["confidence"] == 0.9

def test_intent_engine_delete_file():
    engine = IntentEngine()
    result = engine.parse("delete file")
    assert result["intent"] == "delete_action"
    assert result["domain"] == "system"
    assert result["confidence"] == 0.9

def test_intent_engine_unknown():
    engine = IntentEngine()
    result = engine.parse("fly to the moon")
    assert result["intent"] == "unknown"
    assert result["confidence"] == 0.3
