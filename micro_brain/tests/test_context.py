import pytest
from datetime import datetime
from unittest.mock import MagicMock
from micro_brain.core.context_engine import ContextEngine

def test_context_engine_time_categorization():
    engine = ContextEngine()
    memory_manager = MagicMock()
    memory_manager.get_recent.return_value = []

    # Mocking datetime to test different hours
    with patch("micro_brain.core.context_engine.datetime") as mock_date:
        # Morning: 8 AM
        mock_date.now.return_value = datetime(2025, 1, 1, 8, 0)
        ctx = engine.build(memory_manager)
        assert ctx["time_of_day"] == "morning"

        # Afternoon: 2 PM
        mock_date.now.return_value = datetime(2025, 1, 1, 14, 0)
        ctx = engine.build(memory_manager)
        assert ctx["time_of_day"] == "afternoon"

        # Evening: 7 PM
        mock_date.now.return_value = datetime(2025, 1, 1, 19, 0)
        ctx = engine.build(memory_manager)
        assert ctx["time_of_day"] == "evening"

        # Night: 11 PM
        mock_date.now.return_value = datetime(2025, 1, 1, 23, 0)
        ctx = engine.build(memory_manager)
        assert ctx["time_of_day"] == "night"

def test_context_engine_memory_integration():
    engine = ContextEngine()
    memory_manager = MagicMock()

    mock_memories = [
        {"command": {"action": "open_app"}, "intent": {"intent": "open_app"}},
        {"command": {"action": "generate_report"}, "intent": {"intent": "create_report"}}
    ]
    memory_manager.get_recent.return_value = mock_memories

    ctx = engine.build(memory_manager)
    assert ctx["recent_actions"] == ["open_app", "generate_report"]
    assert ctx["last_intent"]["intent"] == "create_report"

from unittest.mock import patch
