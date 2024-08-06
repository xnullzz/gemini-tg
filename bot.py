import asyncio
import logging
import os
import re
import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from utility.tools import escape_markdown
from IPython.display import Markdown

from dotenv import load_dotenv

from gemini_api import GeminiAPI

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = AsyncTeleBot(TELEGRAM_BOT_TOKEN)
gemini_api = GeminiAPI(api_key=GEMINI_API_KEY)


@bot.message_handler(commands=['start'])
async def cmd_start(message: Message):
    await bot.reply_to(message, "Hello! I'm your Gemini-powered bot.")


@bot.message_handler(commands=['help'])
async def cmd_help(message: Message):
    await bot.reply_to(message, "Help message goes here.")


@bot.message_handler(func=lambda message: True)
async def handle_message(message: Message):
    last_chunk_received = False
    user_message = message.text
    response = await gemini_api.generate_text(prompt=user_message)

    try:
        escaped_response = escape_markdown(response)
        await bot.reply_to(message, response, parse_mode="MarkdownV2")

    except Exception as e:
        logger.error(f"Error sending message: {e}")
        await bot.reply_to(message, "I encountered an error while processing your request. Please try again.")

    if not last_chunk_received:
                bot.send_chat_action(message.chat.id, 'typing')
                last_chunk_received = True

async def main():
    await bot.polling(non_stop=True)


if __name__ == '__main__':
    asyncio.run(main())

