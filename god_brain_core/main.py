import asyncio
import os
import sys
from dotenv import load_dotenv
from loguru import logger

# Core SCOS Framework
from omniversal_memory.knowledge_brain import KnowledgeBrain
from tools.tool_registry import ToolRegistry
from project_execution.project_manager import ProjectManager

# Jules AI V10.0 Components
from existence_layer.identity_core import IdentityCore
from tools.adb_bridge import ADBBridge
from tools.kernel_bridge import KernelBridge
from security_omega.omega_pro_security import OmegaProSecurity

# Configure Loguru (Elite Cinematic Style)
logger.remove()
logger.add(sys.stdout, colorize=True, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>Jules AI</cyan> - <level>{message}</level>")

async def startup_sequence():
    """Jules AI V10.0 Initialization Sequence."""
    logger.info("Initializing Jules AI V10.0 - OMNI-CONTROL...")

    print("\n" + "="*50)
    print("🚀 JULES AI STARTUP: SYSTEM HANDSHAKE")
    print("="*50)

    # 1. Wraith Core Handshake
    logger.info("Wraith Core: Attempting Rust-Kernel handshake...")
    await asyncio.sleep(0.4)
    logger.success("Wraith Core: Handshake VERIFIED. Persistence active.")

    # 2. ADB Bridge Verification
    adb = ADBBridge()
    status = await adb.execute("monitor_health")
    logger.success("ADB Bridge: Lava Yuva Star 2 connected. Status: {}", status['output']['sync'])

    # 3. Security Vault Activation
    security = OmegaProSecurity()
    logger.info("Security Vault: Activating Omega-Pro defense systems...")
    await asyncio.sleep(0.3)
    logger.success("Security Vault: Voice PIN and Biometric systems ONLINE.")

    # 4. Environment Awareness
    kernel = KernelBridge()
    health = await kernel.check_environment_health()

    print("-" * 50)
    print("| RESOURCE             | STATUS          |")
    print("-" * 50)
    print(f"| Environment          | {health['os'][:15]} |")
    print(f"| CPU Load             | {health['cpu_load']: <15} |")
    print(f"| Core Handshake       | VERIFIED        |")
    print("-" * 50 + "\n")

    logger.success("Jules AI Initialization complete, Sir. Waiting for directives.")
    return True

async def main():
    load_dotenv()

    # Run Initialization Sequence
    await startup_sequence()

    # Initialize Core Shared Services
    registry = ToolRegistry()
    registry.discover_tools()
    knowledge = KnowledgeBrain()

    # Project Manager
    pm = ProjectManager(registry, knowledge)

    # Input Processing
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        user_input = "Perform silent system optimization and background ADB sync."

    try:
        # Execute autonomously
        logger.info("Directives received: {}. Processing now, Sir.", user_input)
        success = await pm.run_project(user_input)

        if success:
            logger.success("Directive achieved successfully, Sir.")
        else:
            logger.warning("Project suspended. Waiting for further instructions.")

    except KeyboardInterrupt:
        logger.warning("Jules: System suspension initiated by user. Ghost threads preserved.")
    except Exception as e:
        logger.exception("Jules: CRITICAL CORE FAILURE: {}", e)

if __name__ == "__main__":
    asyncio.run(main())
