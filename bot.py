import asyncio
import logging
import os
from typing import List, Dict
import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message
from cachetools import TTLCache
from utility.tools import parse_markdown, split_long_message
from utility.decorators import authorized_only, rate_limit
from utility.system_prompt import SystemPromptManager
from dotenv import load_dotenv
from gemini_api import GeminiAPI
from utility.file_handler import handle_file  # Import the new file handler

# Load environment variables
load_dotenv()

# Initialize the SystemPromptManager
prompt_manager = SystemPromptManager()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize bot and API
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ALLOWED_USERNAMES = set(os.getenv("ALLOWED_USERNAMES", "").split(","))

bot = AsyncTeleBot(TELEGRAM_BOT_TOKEN)
gemini_api = GeminiAPI(api_key=GEMINI_API_KEY)

# Initialize cache for chat history
chat_history = TTLCache(maxsize=1000, ttl=3600)  # Store 1000 chat histories for 1 hour


@bot.message_handler(commands=['start', 'help'])
async def handle_start_help(message: Message) -> None:
    await bot.reply_to(message, "Send me a message and I'll try my best to respond!")


@bot.message_handler(commands=['set_prompt'])
@authorized_only(bot, ALLOWED_USERNAMES)
async def handle_set_prompt(message: Message) -> None:
    chat_id = message.chat.id
    try:
        new_prompt = message.text.split(' ', 1)[1]
        prompt_manager.set_prompt(chat_id, new_prompt)
        await bot.reply_to(message, f"System prompt set to:\n```\n{new_prompt}\n```", parse_mode="MarkdownV2")
    except IndexError:
        await bot.reply_to(message, "Please provide a prompt after the command, e.g., `/set_prompt You are a helpful assistant.`")


@bot.message_handler(commands=['get_prompt'])
@authorized_only(bot, ALLOWED_USERNAMES)
async def handle_get_prompt(message: Message) -> None:
    chat_id = message.chat.id
    current_prompt = prompt_manager.get_prompt(chat_id)
    await bot.reply_to(message, f"Current system prompt:\n```\n{current_prompt}\n```", parse_mode="MarkdownV2")


@bot.message_handler(commands=['clear_prompt'])
@authorized_only(bot, ALLOWED_USERNAMES)
async def handle_clear_prompt(message: Message) -> None:
    chat_id = message.chat.id
    prompt_manager.clear_prompt(chat_id)
    await bot.reply_to(message, "System prompt cleared.")


@bot.message_handler(func=lambda message: True)
@authorized_only(bot, ALLOWED_USERNAMES)
@rate_limit(limit=20, period=60)
async def handle_message(message: Message) -> None:
    chat_id = message.chat.id

    # Handle files first
    file_response = handle_file(message, GEMINI_API_KEY, bot)  # Pass bot to the function
    if file_response:
        await bot.reply_to(message, file_response)
        return

    # If no file, handle text message
    user_message = message.text

    if chat_id not in chat_history:
        chat_history[chat_id] = []

    chat_history[chat_id].append({"role": "user", "parts": [user_message]})

    try:
        system_prompt = prompt_manager.get_prompt(chat_id)
        response = await gemini_api.generate_chat(chat_history[chat_id], system_prompt)
        chat_history[chat_id].append({"role": "model", "parts": [response]})

        escaped_response = parse_markdown(response)

        # Split the response into smaller chunks if it exceeds the Telegram message limit
        message_parts = split_long_message(escaped_response)

        for part in message_parts:
            await bot.reply_to(message, part, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await bot.reply_to(
            message,
            "I encountered an error while processing your request. Please try again later.",
        )


async def main():
    try:
        await bot.polling(non_stop=True, interval=0, request_timeout=60)
    except Exception as e:
        logger.error(f"Error during bot polling: {e}")

if __name__ == '__main__':
    asyncio.run(main())
