import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.formatting import *

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

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

gemini_api = GeminiAPI(api_key=GEMINI_API_KEY)


@dp.message(Command(commands=['start']))
async def cmd_start(message: Message):
    await message.answer("Hello! I'm your Gemini-powered bot.")


@dp.message(Command(commands=['help']))
async def cmd_help(message: Message):
    await message.answer("Help message goes here.")


@dp.message()
async def handle_message(message: Message):
    user_message = message.text
    response = await gemini_api.generate_text(prompt=user_message)

    try:
        # Use aiogram.utils.formatting.Text to handle markdown
        text = Text(response)
        await message.answer(text.as_markdown())

    except Exception as e:
        logger.error(f"Error sending message: {e}")
        await message.answer("I encountered an error while processing your request. Please try again.")


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
