from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from todoist_client import TodoistClient
from langgraph.checkpoint.memory import MemorySaver
import logging
from nodes import AgentNodes
from state import State

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

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
        # Initialize state graph
        logger.debug("Initializing StateGraph")
        builder = StateGraph(State)
        
        # Initialize Todoist client
        logger.debug("Creating Todoist client")
        todoist_client = TodoistClient()

        # Create nodes instance
        logger.debug("Creating AgentNodes instance")
        nodes = AgentNodes(todoist_client)
        logger.info("Successfully initialized core components")

        # Add nodes to the graph
        logger.debug("Adding nodes to graph")
        builder.add_node("get_tasks", nodes.get_tasks)
        builder.add_node("chat", nodes.chat)
        logger.debug("Successfully added nodes to graph")

        # Configure the graph edges
        logger.debug("Configuring graph edges")
        builder.add_edge(START, "get_tasks")
        builder.add_edge("get_tasks", "chat")
        builder.add_edge("chat", END)
        logger.debug("Successfully configured graph edges")

        # Compile with checkpointing
        logger.debug("Compiling graph with MemorySaver checkpointing")
        compiled_graph = builder.compile(checkpointer=MemorySaver())
        
        logger.info("Successfully created and compiled agent graph")
        return compiled_graph

    except Exception as e:
        logger.error(
            "Failed to create agent", 
            exc_info=True,
            extra={
                "error_type": type(e).__name__,
                "error_details": str(e)
            }
        )
        raise
