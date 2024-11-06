import asyncio
import logging
from typing import Dict, Any
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, User
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import os
from dotenv import load_dotenv
from aiogram.client.default import DefaultBotProperties
from .agent_handler import handle_agent_interaction
from ..agent import create_agent
from .logging_setup import setup_logging
from .supabase_client import SupabaseClient

# Initialize logging
logger = setup_logging("my_coach")
logger.info("Starting Telegram bot application")

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    logger.critical("TELEGRAM_BOT_TOKEN not found in environment variables")
    raise ValueError("TELEGRAM_BOT_TOKEN must be set in environment variables")


class UserStates(StatesGroup):
    chatting = State()
    waiting_first_name = State()


# Initialize components
logger.info("Initializing bot components")
try:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    supabase = SupabaseClient()
    logger.info("Bot and dispatcher successfully initialized")
except Exception as e:
    logger.critical("Failed to initialize bot components", exc_info=True)
    raise

# Store user-specific graphs
user_graphs: Dict[int, Any] = {}

@dp.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    """Handle the /start command"""
    user: User = message.from_user
    if not user:
        logger.warning("Received /start command without user information")
        return

    user_id = user.id
    first_name = user.first_name

    try:
        # Store initial user data in state
        await state.update_data(telegram_id=user_id)
        
        # Check if first name is missing
        if not first_name:
            await state.set_state(UserStates.waiting_first_name)
            await message.answer("Please tell me your first name.")
            return

        # If we have first name, proceed with normal flow
        await initialize_user_session(message, state, user_id, first_name)

    except Exception as e:
        logger.error(
            f"Failed to initialize session for user {user_id}",
            exc_info=True,
            extra={"user_id": user_id, "first_name": first_name},
        )
        await message.answer(
            "Sorry, there was an error initializing your session. Please try again later."
        )

@dp.message(UserStates.waiting_first_name)
async def process_first_name(message: Message, state: FSMContext) -> None:
    """Handle first name collection"""
    if not message.text:
        await message.answer("Please send me your first name as text.")
        return
    
    first_name = message.text
    user_data = await state.get_data()
    
    # Initialize user session with collected data
    await initialize_user_session(
        message, 
        state,
        user_data["telegram_id"],
        first_name
    )

# Helper function to initialize user session
async def initialize_user_session(
    message: Message,
    state: FSMContext,
    user_id: int,
    first_name: str
) -> None:
    """Initialize user session with complete user data"""
    # Check if user exists in Supabase
    existing_user = await supabase.get_user(user_id)
    
    if not existing_user:
        # Create new user
        await supabase.create_user(
            telegram_id=user_id,
            first_name=first_name
        )
    
    # Initialize chat
    user_graphs[user_id] = create_agent()
    await state.set_state(UserStates.chatting)
    
    welcome_msg = (
        f"Welcome {hbold(first_name)}! 👋\n"
        "I'm your personal development coach. I can help you with:\n"
        "- Goal setting and achievement\n"
        "- Motivation and habit formation\n"
        "- Personal growth\n\n"
        "How can I help you today?"
    )
    await message.answer(welcome_msg)
    logger.info(f"Successfully initialized session for user {user_id}")

@dp.message(UserStates.chatting)
async def handle_message(message: Message, state: FSMContext) -> None:
    """Handle chat messages"""
    if not message.from_user:
        logger.warning("Received message without user information")
        return

    user_id = message.from_user.id
    message_preview = message.text[:50] + "..." if message.text else "No text"
    logger.info(f"Processing message from user {user_id}")
    logger.debug(f"Message preview: {message_preview}")

    try:
        if user_id not in user_graphs:
            logger.debug(f"Creating new agent for user {user_id}")
            user_graphs[user_id] = create_agent()

        async def send_message(content: str):
            await message.answer(content)
            logger.debug(f"Sent response to user {user_id}")

        async def show_typing():
            await bot.send_chat_action(chat_id=message.chat.id, action="typing")
            logger.debug(f"Showing typing indicator to user {user_id}")

        await handle_agent_interaction(
            message_text=message.text or "",
            graph=user_graphs[user_id],
            send_message=send_message,
            show_typing=show_typing,
            user_id=str(user_id),
        )
        logger.info(f"Successfully processed message from user {user_id}")

    except Exception as e:
        logger.error(
            f"Failed to process message from user {user_id}",
            exc_info=True,
            extra={"user_id": user_id, "message_preview": message_preview},
        )
        await message.answer(
            "Sorry, I encountered an error processing your message. Please try again."
        )

if __name__ == "__main__":
    logger.info("Starting bot polling")
    try:
        asyncio.run(dp.start_polling(bot))
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.critical("Failed to start bot polling", exc_info=True)
        raise
    finally:
        logger.info("Shutdown complete")
