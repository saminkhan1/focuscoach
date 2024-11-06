from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
import logging
from .utils.todoist import TodoistClient
from .nodes.chat import ChatNode
from .nodes.get_tasks import GetTasksNode
from .state import State
from .utils.logging_setup import setup_logging

# Load environment variables
load_dotenv()

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)  # Get module-specific logger


def create_agent():
    """
    Creates and configures the agent graph with Todoist integration.

    Returns:
        Compiled StateGraph instance with memory persistence

    Raises:
        Exception: If there's an error during agent creation
    """
    logger.info("Starting agent creation")
    try:
        # Initialize components
        todoist_client = TodoistClient()
        get_tasks_node = GetTasksNode(todoist_client)
        chat_node = ChatNode()

        # Create workflow
        workflow = StateGraph(State)

        # Add nodes to the graph
        workflow.add_node("get_tasks", get_tasks_node)
        workflow.add_node("chat_node", chat_node)

        # Define edges
        workflow.add_edge("get_tasks", "chat_node")
        workflow.add_edge("chat_node", END)

        # Set entry point
        workflow.set_entry_point("get_tasks")

        # Compile graph
        compiled_graph = workflow.compile(checkpointer=MemorySaver())
        logger.info("Agent created successfully")

        return compiled_graph

    except Exception as e:
        logger.error("Failed to create agent", exc_info=True)
        raise
