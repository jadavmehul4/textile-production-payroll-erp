import pytest
import asyncio
from micro_brain.core.event_bus import EventBus

@pytest.mark.asyncio
async def test_event_bus_emit_receive():
    bus = EventBus()
    received_data = []

    async def handler(data):
        received_data.append(data)

    bus.register("test_event", handler)
    await bus.emit("test_event", "hello")

    assert received_data == ["hello"]

@pytest.mark.asyncio
async def test_event_bus_multiple_handlers():
    bus = EventBus()
    count = 0

    async def handler1(data):
        nonlocal count
        count += 1

    async def handler2(data):
        nonlocal count
        count += 1

    bus.register("increment", handler1)
    bus.register("increment", handler2)
    await bus.emit("increment")

    assert count == 2
