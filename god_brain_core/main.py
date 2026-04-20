import asyncio
import os
import sys
from dotenv import load_dotenv
from loguru import logger

# Core Framework
from omniversal_memory.knowledge_brain import KnowledgeBrain
from tools.tool_registry import ToolRegistry
from project_execution.project_manager import ProjectManager

# Configure Loguru
logger.remove()
logger.add(sys.stdout, colorize=True, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>")

async def main():
    load_dotenv()

    # Initialize Core Shared Services
    registry = ToolRegistry()
    registry.discover_tools()

    knowledge = KnowledgeBrain()

    # Project Manager is the new primary entry point for Phase 6
    pm = ProjectManager(registry, knowledge)

    # 1. Handle command line goal
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        user_input = "Build a multi-agent diagnostic framework for cognitive systems."

    logger.info("Starting Ω GOD_BRAIN_CORE_Ω with Project Autonomy (Phase 6)")

    try:
        # Run the project autonomously until completion or failure
        success = await pm.run_project(user_input)

        if success:
            logger.success("Ω System has achieved the goal.")
        else:
            logger.error("Ω System suspended project. Check logs for details.")

    except KeyboardInterrupt:
        logger.warning("Project interrupted by user. Checkpoints preserved.")
    except Exception as e:
        logger.exception("CRITICAL SYSTEM FAILURE: {}", e)

if __name__ == "__main__":
    asyncio.run(main())
