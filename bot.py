import asyncio
import logging
import os
import re
from typing import List, Tuple

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.markdown import escape_md

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

def process_markdown(text: str) -> Tuple[str, List[Tuple[int, int]]]:
    """
    Process markdown to handle bold, italic, and bullet points.
    Returns the processed text and a list of entity tuples.
    """
    entities = []
    lines = text.split('\n')
    processed_lines = []

    for line in lines:
        if line.strip().startswith('* '):
            processed_line = '• ' + line.strip()[2:]
        else:
            processed_line = line

        # Process bold and italic
        offset = 0
        while '**' in processed_line or '*' in processed_line:
            bold_start = processed_line.find('**')
            italic_start = processed_line.find('*')

            if bold_start != -1 and (italic_start == -1 or bold_start < italic_start):
                bold_end = processed_line.find('**', bold_start + 2)
                if bold_end != -1:
                    entities.append((len(''.join(processed_lines)) + offset + bold_start, bold_end - bold_start - 2, 'bold'))
                    processed_line = processed_line[:bold_start] + processed_line[bold_start+2:bold_end] + processed_line[bold_end+2:]
                    offset -= 4
                else:
                    break
            elif italic_start != -1:
                italic_end = processed_line.find('*', italic_start + 1)
                if italic_end != -1:
                    entities.append((len(''.join(processed_lines)) + offset + italic_start, italic_end - italic_start - 1, 'italic'))
                    processed_line = processed_line[:italic_start] + processed_line[italic_start+1:italic_end] + processed_line[italic_end+1:]
                    offset -= 2
                else:
                    break

        processed_lines.append(processed_line)

    return '\n'.join(processed_lines), entities

@dp.message(Command(commands=['start']))
async def cmd_start(message: Message):
    await message.answer("Hello! I'm your Gemini-powered bot.")

@dp.message(Command(commands=['help']))
async def cmd_help(message: Message):
    await message.answer("Help message goes here.")

@dp.message()
async def handle_message(message: Message):
    user_message = message.text
    response = gemini_api.generate_text(prompt=user_message)

    processed_text, entities = process_markdown(response)
    escaped_text = escape_md(processed_text)

    try:
        await message.answer(escaped_text, parse_mode=ParseMode.MARKDOWN_V2, entities=entities)
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        await message.answer("I encountered an error while processing your request. Please try again.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
