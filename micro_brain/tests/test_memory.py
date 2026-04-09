import pytest
from micro_brain.memory.memory_manager import MemoryManager

def test_memory_manager_add_and_retrieve():
    manager = MemoryManager(limit=5)

    for i in range(3):
        manager.add({"data": i})

    recent = manager.get_recent(limit=2)
    assert len(recent) == 2
    assert recent[0]["data"] == 1
    assert recent[1]["data"] == 2
    assert "timestamp" in recent[0]

def test_memory_manager_limit():
    manager = MemoryManager(limit=3)

    for i in range(5):
        manager.add({"data": i})

    all_mem = manager.get_recent(limit=10)
    assert len(all_mem) == 3
    # Should contain 2, 3, 4 (0 and 1 were removed)
    assert all_mem[0]["data"] == 2
    assert all_mem[2]["data"] == 4
