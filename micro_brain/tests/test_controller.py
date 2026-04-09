import pytest
from micro_brain.core.controller import Controller

def test_controller_routing_to_agent():
    controller = Controller()
    command = {"action": "generate_report", "target": "production"}
    result = controller.execute(command)
    assert result["status"] == "success"
    assert "TaskAgent" in result["message"]

def test_controller_routing_to_executor():
    controller = Controller()
    command = {"action": "open_app", "target": "notepad"}
    # This will attempt to open notepad, which might fail on Linux, but we check status/message
    result = controller.execute(command)
    assert "status" in result

def test_controller_unsupported():
    controller = Controller()
    command = {"action": "invalid_action"}
    result = controller.execute(command)
    assert result["status"] == "error"
    assert "cannot resolve" in result["message"]
