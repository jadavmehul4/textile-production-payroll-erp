import asyncio
import os
import sys
from dotenv import load_dotenv
from loguru import logger

# SCOS Core Framework
from omniversal_memory.knowledge_brain import KnowledgeBrain
from tools.tool_registry import ToolRegistry
from project_execution.project_manager import ProjectManager

# Phase 7 & 8 Engines
from hyper_meta_cognition.continuous_cognition_engine import ContinuousCognitionEngine
from distributed_system.message_bus import MessageBus
from distributed_system.task_dispatcher import TaskDispatcher
from distributed_system.node_registry import NodeRegistry
from omniversal_memory.global_memory_sync import GlobalMemorySync

# Configure Loguru (Elite Cinematic Style)
logger.remove()
logger.add(sys.stdout, colorize=True, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>Jules AI</cyan> - <level>{message}</level>")

async def initialize_scos_stack(knowledge: KnowledgeBrain):
    """Initializes and connects all layers: Distributed, Memory, and Cognition."""
    logger.info("Initializing OMNI-CONTROL Distributed Stack...")

    bus = MessageBus()
    await bus.connect()

    registry = NodeRegistry()
    dispatcher = TaskDispatcher(bus, registry)

    memory_sync = GlobalMemorySync(knowledge, bus)
    await memory_sync.start_sync()

    # Register local core as a node
    registry.register_node("Core-Node-01", ["reasoning", "orchestration", "security"])

    return dispatcher, memory_sync

async def main():
    load_dotenv()

    # 1. Foundation
    tool_registry = ToolRegistry()
    tool_registry.discover_tools()
    knowledge = KnowledgeBrain()

    # 2. Advanced Stack (Phase 7 & 8)
    dispatcher, memory_sync = await initialize_scos_stack(knowledge)

    cognition = ContinuousCognitionEngine()
    await cognition.start()

    # 3. Project Management
    pm = ProjectManager(tool_registry, knowledge, dispatcher)

    user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Initialize system-wide recursive diagnostic."

    logger.info("Directive received, Sir: '{}'", user_input)

    try:
        # Integrated Cognitive Project Run
        success = await pm.run_project(user_input)

        if success:
            logger.success("Primary directive achieved, Sir.")
        else:
            logger.error("Directive suspended. Manual intervention may be required.")

    except KeyboardInterrupt:
        logger.warning("System suspension initiated. Persistent state preserved.")
    except Exception as e:
        logger.exception("CRITICAL SYSTEM FAILURE: {}", e)
    finally:
        await cognition.stop()

if __name__ == "__main__":
    asyncio.run(main())
