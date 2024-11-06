import os
from supabase.client import create_client, Client
from dotenv import load_dotenv
import logging
from .logging_setup import setup_logging
from typing import Optional, Dict, Any

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)


class SupabaseClient:
    def __init__(self):
        load_dotenv()
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")

        if not self.url or not self.key:
            logger.critical("Supabase credentials not found in environment variables")
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
            )

        self.client: Client = create_client(self.url, self.key)
        logger.info("Supabase client initialized")

    async def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user by Telegram ID
        Args:
            telegram_id: Unique identifier for Telegram user
        Returns:
            Optional[Dict[str, Any]]: User data or None if not found
        """
        try:
            response = self.client.table('users').select("*").eq('id', telegram_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting user {telegram_id}", exc_info=True)
            raise

    async def create_user(self, telegram_id: int, first_name: str) -> Dict[str, Any]:
        """
        Create new user from Telegram data
        Args:
            telegram_id: Unique identifier for Telegram user
            first_name: User's first name from Telegram
        Returns:
            Dict[str, Any]: Created user data
        """
        try:
            data = {
                'id': telegram_id,
                'first_name': first_name
            }
            response = self.client.table('users').insert(data).execute()
            logger.info(f"Created new user: {telegram_id}")
            return response.data[0]
        except Exception as e:
            logger.error(f"Error creating user {telegram_id}", exc_info=True)
            raise

    async def update_user(self, telegram_id: int, **kwargs) -> Dict[str, Any]:
        """
        Update user data
        Args:
            telegram_id: Unique identifier for Telegram user
            **kwargs: Fields to update (e.g., first_name, last_name, age, occupation)
        Returns:
            Dict[str, Any]: Updated user data
        """
        try:
            response = self.client.table('users').update(kwargs).eq('telegram_id', telegram_id).execute()
            logger.info(f"Updated user {telegram_id}: {kwargs}")
            return response.data[0]
        except Exception as e:
            logger.error(f"Error updating user {telegram_id}", exc_info=True)
            raise
