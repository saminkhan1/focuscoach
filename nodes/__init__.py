import logging
from .chat import ChatNode
from .get_tasks import GetTasksNode

logger = logging.getLogger(__name__)


class AgentNodes:
    def __init__(self, todoist_client):
        logger.info("Initializing AgentNodes")
        try:
            self.get_tasks_node = GetTasksNode(todoist_client)
            self.chat_node = ChatNode()
            logger.info("Successfully initialized all nodes")
        except Exception as e:
            logger.error(f"Failed to initialize AgentNodes: {str(e)}", exc_info=True)
            raise

    @property
    def get_tasks(self):
        return self.get_tasks_node.__call__

    @property
    def chat(self):
        return self.chat_node.__call__
