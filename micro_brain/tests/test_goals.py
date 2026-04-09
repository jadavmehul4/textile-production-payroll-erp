import pytest
from micro_brain.core.goal_engine import GoalEngine

def test_goal_engine_frequent_action():
    engine = GoalEngine()
    learning_data = {"frequent_actions": ["open_app"]}
    context = {"time_of_day": "afternoon"}

    result = engine.generate(learning_data, context)
    assert "Optimize application usage" in result["goals"]
    assert "Suggest auto-launch for frequent apps" in result["actions"]

def test_goal_engine_morning_context():
    engine = GoalEngine()
    learning_data = {"frequent_actions": []}
    context = {"time_of_day": "morning"}

    result = engine.generate(learning_data, context)
    assert "Maximize morning productivity" in result["goals"]
    assert "Prepare dashboard for daily review" in result["actions"]

def test_goal_engine_intent_bias():
    engine = GoalEngine()
    learning_data = {"frequent_actions": []}
    context = {
        "time_of_day": "afternoon",
        "last_intent": {"domain": "production"}
    }

    result = engine.generate(learning_data, context)
    assert "Monitor production efficiency" in result["goals"]
    assert "Enable real-time production alerts" in result["actions"]
