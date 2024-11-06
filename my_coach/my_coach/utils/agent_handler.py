import logging
from typing import Any, Optional, Callable

# Configure logging
logger = logging.getLogger(__name__)


async def handle_agent_interaction(
    message_text: str,
    graph: Any,
    send_message: Callable[[str], Any],
    show_typing: Optional[Callable[[], Any]] = None,
    user_id: str = "",
) -> None:
    """
    Handle interaction with the LangGraph agent.

    Args:
        message_text: The user's message text
        graph: User-specific graph instance
        send_message: Async callback to send messages back to the user
        show_typing: Optional callback to show typing indicator
        user_id: Unique identifier for the user (from Telegram)
    """
    logger.info(f"Starting agent interaction for user_id: {user_id}")
    logger.debug(f"Received message: {message_text[:100]}...")  # Truncate long messages
    
    try:
        # Configure thread ID for state management
        config = {
            "configurable": {
                "thread_id": str(user_id),
            }
        }
        logger.debug(f"Configured thread with ID: {user_id}")

        new_message = {"role": "user", "msgs": message_text}
        
        # Show typing indicator if callback provided
        if show_typing:
            logger.debug("Activating typing indicator")
            await show_typing()

        final_content = ""
        logger.debug("Starting message stream processing")

        # Use user-specific graph instance with config
        async for chunk in graph.astream(new_message, config, stream_mode="values"):
            if "msgs" in chunk:
                last_event = chunk["msgs"][-1]
                if last_event.content:
                    final_content = last_event.content
                    logger.debug("Received content chunk from stream")

        logger.debug("Stream processing completed")
        
        if final_content:
            logger.info(f"Successfully generated response for user {user_id}")
            logger.debug(f"Response content (truncated): {final_content[:100]}...")
        else:
            logger.warning(f"Empty response generated for user {user_id}")

        await send_message(final_content)
        logger.info(f"Response sent to user {user_id}")

    except Exception as e:
        error_msg = "Sorry, I encountered an error. Please try again later."
        logger.error(
            f"Error in agent interaction for user {user_id}: {str(e)}", 
            exc_info=True,
            extra={
                "user_id": user_id,
                "message_text": message_text[:100],  # Truncate for logging
            }
        )
        await send_message(error_msg)
        logger.info(f"Error message sent to user {user_id}")
