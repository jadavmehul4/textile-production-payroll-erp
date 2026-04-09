import pytest
from micro_brain.agents.task_agent import TaskAgent
from micro_brain.agents.agent_manager import AgentManager

def test_task_agent_generate_report():
    agent = TaskAgent()
    command = {"action": "generate_report", "target": "production"}
    # We mock sleep for faster testing in real scenarios, but here we just check result
    result = agent.execute(command)
    assert result["status"] == "success"
    assert "completed by TaskAgent" in result["message"]

def test_agent_manager_selection():
    manager = AgentManager()

    # Should return TaskAgent
    cmd_report = {"action": "generate_report", "target": "general"}
    agent = manager.get_agent(cmd_report)
    assert agent is not None
    assert agent.name == "TaskAgent"

    # Should return None
    cmd_open = {"action": "open_app", "target": "excel"}
    assert manager.get_agent(cmd_open) is None
