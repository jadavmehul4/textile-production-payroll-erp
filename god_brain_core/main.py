import asyncio
import os
import sys
from dotenv import load_dotenv
from loguru import logger

# Core Framework
from omniversal_memory.knowledge_brain import KnowledgeBrain
from tools.tool_registry import ToolRegistry
from project_execution.project_manager import ProjectManager

# Phase 7 Modules
from hyper_meta_cognition.continuous_cognition_engine import ContinuousCognitionEngine
from distributed_system.message_bus import MessageBus
from distributed_system.brain_node import BrainNode
from distributed_system.task_dispatcher import TaskDispatcher
from distributed_system.node_registry import NodeRegistry
from omniversal_memory.global_memory_sync import GlobalMemorySync
from infrastructure.task_runner import TaskRunner

# Configure Loguru
logger.remove()
logger.add(sys.stdout, colorize=True, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>")

async def initialize_distributed_network(kb: KnowledgeBrain):
    """Sets up the distributed environment and synchronization."""
    bus = MessageBus()
    await bus.connect()

    registry = NodeRegistry()
    dispatcher = TaskDispatcher(bus)
    sync = GlobalMemorySync(kb, bus)
    await sync.start_sync()

    # Spawn two local worker nodes for demonstration
    node1 = BrainNode("Node-Alpha")
    node2 = BrainNode("Node-Beta")

    await node1.start()
    await node2.start()

    registry.register_node("Node-Alpha", ["reasoning", "coding"])
    registry.register_node("Node-Beta", ["search", "file_io"])

    return dispatcher, sync

async def main():
    load_dotenv()

    # 1. Initialize Core Services
    tool_registry = ToolRegistry()
    tool_registry.discover_tools()

    knowledge = KnowledgeBrain()

    logger.info("Starting Ω GOD_BRAIN_CORE_Ω Phase 7: Continuous & Distributed")

    # 2. Start Background Cognition
    cognition = ContinuousCognitionEngine()
    await cognition.start()

    # 3. Setup Distributed Network
    dispatcher, memory_sync = await initialize_distributed_network(knowledge)

    # 4. Project Management (Orchestrator)
    pm = ProjectManager(tool_registry, knowledge)

    # 5. Handle Input
    user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Develop a distributed neural architecture."

    try:
        # Initial Memory Broadcast
        await memory_sync.broadcast_update(f"System initialized for goal: {user_input}", "Core")

        # Execute project autonomously
        success = await pm.run_project(user_input)

        if success:
            logger.success("Goal Achieved: {}", user_input)
        else:
            logger.error("Project suspended.")

    except KeyboardInterrupt:
        logger.warning("System shutdown requested.")
    except Exception as e:
        logger.exception("CRITICAL ERROR: {}", e)
    finally:
        await cognition.stop()

if __name__ == "__main__":
    asyncio.run(main())
