import asyncio
from loguru import logger

class NodeRegistry:
    """Tracks active brain nodes in the distributed network."""

    def __init__(self):
        self.nodes = {}

    def register_node(self, node_id: str, capabilities: list):
        self.nodes[node_id] = {
            "capabilities": capabilities,
            "status": "online",
            "last_heartbeat": asyncio.get_event_loop().time()
        }
        logger.info("DISTRIBUTED: Node {} registered with capabilities: {}", node_id, capabilities)

    def get_active_nodes(self):
        return [node_id for node_id, data in self.nodes.items() if data["status"] == "online"]

    def unregister_node(self, node_id: str):
        if node_id in self.nodes:
            del self.nodes[node_id]
            logger.info("DISTRIBUTED: Node {} unregistered.", node_id)
