import pytest
from unittest.mock import MagicMock
from micro_brain.core.learning_engine import LearningEngine

def test_learning_engine_pattern_detection():
    engine = LearningEngine()
    memory_manager = MagicMock()

    # 3 occurrences of 'open_app', 2 of 'generate_report'
    mock_memories = [
        {"command": {"action": "open_app"}},
        {"command": {"action": "open_app"}},
        {"command": {"action": "generate_report"}},
        {"command": {"action": "open_app"}},
        {"command": {"action": "generate_report"}}
    ]
    memory_manager.get_recent.return_value = mock_memories

    result = engine.analyze(memory_manager)
    assert "open_app" in result["frequent_actions"]
    assert "generate_report" not in result["frequent_actions"]
    assert any("startup" in s for s in result["suggestions"])

def test_learning_engine_no_patterns():
    engine = LearningEngine()
    memory_manager = MagicMock()
    memory_manager.get_recent.return_value = []

    result = engine.analyze(memory_manager)
    assert result["frequent_actions"] == []
    assert result["suggestions"] == []
