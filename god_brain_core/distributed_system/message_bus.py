import asyncio
import json
from loguru import logger

class MessageBus:
    """Production-grade NATS message bus interface."""

    def __init__(self, nats_url="nats://localhost:4222"):
        self.nats_url = nats_url
        self.nc = None
        self.subscriptions = {}

    async def connect(self):
        """Establishes connection to the NATS cluster."""
        logger.info("DISTRIBUTED: Establishing connection to NATS cluster at {}...", self.nats_url)
        try:
            import nats
            self.nc = await nats.connect(self.nats_url)
            logger.success("DISTRIBUTED: NATS connection verified.")
            return True
        except ImportError:
            logger.warning("NATS client not installed. Falling back to local internal bus.")
            return False
        except Exception as e:
            logger.error("NATS connection failed: {}. Continuous mode active.", e)
            return False

    async def publish(self, topic: str, message: dict):
        """Publishes a structured message to the network."""
        logger.debug("DISTRIBUTED: Publishing to topic '{}'", topic)
        if self.nc and self.nc.is_connected:
            await self.nc.publish(topic, json.dumps(message).encode())
        else:
            # Internal async dispatch simulation
            if topic in self.subscriptions:
                asyncio.create_task(self.subscriptions[topic](message))

    async def subscribe(self, topic: str, callback):
        """Registers a listener for a topic."""
        logger.info("DISTRIBUTED: Subscribing unit to topic '{}'", topic)
        self.subscriptions[topic] = callback
        if self.nc and self.nc.is_connected:
            await self.nc.subscribe(topic, cb=lambda msg: callback(json.loads(msg.data.decode())))

    async def close(self):
        if self.nc:
            await self.nc.close()
