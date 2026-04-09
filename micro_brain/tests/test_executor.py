import pytest
from unittest.mock import patch, MagicMock
from micro_brain.core.action_executor import ActionExecutor

def test_action_executor_generate_report():
    executor = ActionExecutor()
    command = {"action": "generate_report", "target": "production", "priority": "medium"}
    result = executor.execute(command)
    assert result["status"] == "success"
    assert "generated" in result["message"]

def test_action_executor_block_critical():
    executor = ActionExecutor()
    command = {"action": "delete", "target": "system", "priority": "critical"}
    result = executor.execute(command)
    assert result["status"] == "error"
    assert "blocked" in result["message"]

@patch("subprocess.Popen")
def test_action_executor_open_app_linux(mock_popen):
    executor = ActionExecutor()
    command = {"action": "open_app", "target": "excel", "priority": "high"}

    with patch("platform.system", return_value="Linux"):
        result = executor.execute(command)
        assert result["status"] == "success"
        mock_popen.assert_called()

def test_action_executor_unsupported():
    executor = ActionExecutor()
    command = {"action": "fly_to_mars", "target": "mars", "priority": "low"}
    result = executor.execute(command)
    assert result["status"] == "error"
    assert "Unsupported action" in result["message"]
