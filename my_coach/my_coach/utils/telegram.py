import asyncio
import logging
from typing import Dict, Any
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import os
from dotenv import load_dotenv
from aiogram.client.default import DefaultBotProperties
from .agent_handler import handle_agent_interaction
from ..agent import create_agent

# Configure root logger
logging.basicConfig(
    level=logging.INFO,  # Changed to INFO for production
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]",
    handlers=[logging.StreamHandler()],
)

# Get module logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
logger.debug("Environment variables loaded")

# Validate environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    logger.critical("TELEGRAM_BOT_TOKEN not found in environment variables")
    raise ValueError("TELEGRAM_BOT_TOKEN must be set in environment variables")


class UserStates(StatesGroup):
    chatting = State()


# Initialize components
logger.info("Initializing bot components")
try:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    logger.info("Bot and dispatcher successfully initialized")
except Exception as e:
    logger.critical("Failed to initialize bot components", exc_info=True)
    raise

# Store user-specific graphs
user_graphs: Dict[int, Any] = {}


@dp.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    """Handle the /start command"""
    if not message.from_user:
        logger.warning("Received /start command without user information")
        return

    user_id = message.from_user.id
    user_name = message.from_user.full_name
    logger.info(f"Processing /start command for user {user_id} ({user_name})")

    try:
        logger.debug(f"Creating agent for user {user_id}")
        user_graphs[user_id] = create_agent()

        await state.set_state(UserStates.chatting)
        logger.debug(f"Set state to chatting for user {user_id}")

        welcome_message = (
            f"Hello, {hbold(user_name)}! 👋\n\n"
            "I'm your personal development coach. I can help you with:\n"
            "- Goal setting and achievement\n"
            "- Motivation and habit formation\n"
            "- Personal growth\n\n"
            "Feel free to ask me anything or share what's on your mind!"
        )
        await message.answer(welcome_message)
        logger.info(f"Successfully initialized session for user {user_id}")

    except Exception as e:
        logger.error(
            f"Failed to initialize session for user {user_id}",
            exc_info=True,
            extra={"user_id": user_id, "user_name": user_name},
        )
        await message.answer(
            "Sorry, there was an error initializing your session. Please try again later."
        )


@dp.message(Command("help"))
async def command_help(message: Message) -> None:
    """Handle the /help command"""
    if not message.from_user:
        logger.warning("Received /help command without user information")
        return

    user_id = message.from_user.id
    logger.info(f"Processing /help command for user {user_id}")

    help_text = "Just send me a message and I'll be happy to help!"
    await message.answer(help_text)
    logger.debug(f"Sent help message to user {user_id}")


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
        # Initialize graph for new users
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
        logger.info("Bot polling started successfully")
    except Exception as e:
        logger.critical("Failed to start bot polling", exc_info=True)
        raise
