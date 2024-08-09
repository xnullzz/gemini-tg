import asyncio
import logging
import os
from typing import List, Dict
import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message
from cachetools import TTLCache
from utility.tools import parse_markdown
from utility.decorators import authorized_only, rate_limit
from utility.system_prompt import SystemPromptManager
from dotenv import load_dotenv
from gemini_api import GeminiAPI

# Load environment variables
load_dotenv()

# Initialize the SystemPromptManager
prompt_manager = SystemPromptManager()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize bot and API
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ALLOWED_USERNAMES = set(os.getenv("ALLOWED_USERNAMES", "").split(","))

bot = AsyncTeleBot(TELEGRAM_BOT_TOKEN)
gemini_api = GeminiAPI(api_key=GEMINI_API_KEY)

# Initialize cache for chat history
chat_history = TTLCache(maxsize=1000, ttl=3600)  # Store 1000 chat histories for 1 hour

@bot.message_handler(commands=['start'])
@authorized_only(bot, ALLOWED_USERNAMES)
@rate_limit(limit=5, period=60)
async def cmd_start(message: Message) -> None:
    start_message = (
        "Welcome to the Gemini-powered AI assistant! 🤖✨\n\n"
        "I'm here to help you with a wide range of tasks, including:\n"
        "• Answering questions\n"
        "• Providing explanations\n"
        "• Assisting with analysis\n"
        "• Offering creative ideas\n\n"
        "Feel free to ask me anything, and I'll do my best to assist you. "
        "For more information about what I can do, type /help."
    )
    await bot.reply_to(message, start_message)

@bot.message_handler(commands=['help'])
@authorized_only(bot, ALLOWED_USERNAMES)
@rate_limit(limit=5, period=60)
async def cmd_help(message: Message) -> None:
    help_message = (
        "Here's how you can interact with me:\n\n"
        "1. Ask questions on any topic\n"
        "2. Request explanations or clarifications\n"
        "3. Seek assistance with analysis or problem-solving\n"
        "4. Get creative ideas or writing suggestions\n"
        "5. Discuss complex topics or theories\n\n"
        "Commands:\n"
        "/start - Begin interacting with the bot\n"
        "/help - Display this help message\n"
        "/reset_context - Clear your chat history\n\n"
        "/set_prompt - Set system prompt for answers\n\n"
        "/clear_prompt - Set no system prompt for answers"
        "Remember, I'm an AI language model, so my responses are based on my training data. "
        "For the most up-to-date or critical information, always consult authoritative sources."
    )
    await bot.reply_to(message, help_message)

@bot.message_handler(commands=['reset_context'])
@authorized_only(bot, ALLOWED_USERNAMES)
@rate_limit(limit=5, period=60)
async def cmd_reset(message: Message) -> None:
    chat_id = message.chat.id
    if chat_id in chat_history:
        del chat_history[chat_id]
    await bot.reply_to(message, "Your chat history has been cleared.")

@bot.message_handler(commands=['set_prompt'])
@authorized_only(bot, ALLOWED_USERNAMES)
@rate_limit(limit=5, period=60)
async def cmd_set_prompt(message: Message) -> None:
    chat_id = message.chat.id
    prompt_text = message.text.split(' ', 1)[1] if len(message.text.split()) > 1 else ""
    if not prompt_text:
        await bot.reply_to(message, "Please provide a prompt text. Usage: /set_prompt <your_prompt>")
        return

    prompt_manager.set_prompt(chat_id, prompt_text)
    await bot.reply_to(message, "System prompt has been set successfully.")

@bot.message_handler(commands=['get_prompt'])
@authorized_only(bot, ALLOWED_USERNAMES)
@rate_limit(limit=5, period=60)
async def cmd_get_prompt(message: Message) -> None:
    chat_id = message.chat.id
    current_prompt = prompt_manager.get_prompt(chat_id)
    await bot.reply_to(message, f"Current system prompt: {current_prompt}")

@bot.message_handler(commands=['clear_prompt'])
@authorized_only(bot, ALLOWED_USERNAMES)
@rate_limit(limit=5, period=60)
async def cmd_clear_prompt(message: Message) -> None:
    chat_id = message.chat.id
    prompt_manager.clear_prompt(chat_id)
    await bot.reply_to(message, "System prompt has been cleared.")

@bot.message_handler(func=lambda message: True)
@authorized_only(bot, ALLOWED_USERNAMES)
@rate_limit(limit=20, period=60)
async def handle_message(message: Message) -> None:
    chat_id = message.chat.id
    user_message = message.text

    if chat_id not in chat_history:
        chat_history[chat_id] = []

    chat_history[chat_id].append({"role": "user", "parts": [user_message]})

    try:
        system_prompt = prompt_manager.get_prompt(chat_id)
        response = await gemini_api.generate_chat(chat_history[chat_id], system_prompt)
        chat_history[chat_id].append({"role": "model", "parts": [response]})

        escaped_response = parse_markdown(response)
        await bot.reply_to(message, escaped_response, parse_mode="HTML")
    
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await bot.reply_to(message, "I encountered an error while processing your request. Please try again later.")

async def main() -> None:
    try:
        await bot.polling(non_stop=True)
    except Exception as e:
        logger.error(f"Error in main polling loop: {e}")
        await asyncio.sleep(5)
        await main()

if __name__ == '__main__':
    asyncio.run(main())
