import asyncio
import logging
import os
from typing import List, Dict
import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from gemini_api import GeminiAPI, ModelSelector
from cachetools import TTLCache
from utility.formatting import parse_markdown, split_long_message
from utility.decorators import authorized_only, rate_limit
from utility.system_prompt import SystemPromptManager
from dotenv import load_dotenv
from utility.file_handler import handle_file  # Import the new file handler

# Load environment variables
load_dotenv()

# Initialize the SystemPromptManager
prompt_manager = SystemPromptManager()
model_selector = ModelSelector()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize bot and gemini API keys
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ALLOWED_USERNAMES = set(os.getenv("ALLOWED_USERNAMES", "").split(","))

#Initialize the bot
bot = AsyncTeleBot(TELEGRAM_BOT_TOKEN)
def set_commands():
    await bot.set_my_commands([
        BotCommand("/start", "Start the bot"),
        BotCommand("/help", "Show help information"),
        BotCommand("/set_prompt", "Set a custom system prompt"),
        BotCommand("/get_prompt", "View the current system prompt"),
        BotCommand("/clear_prompt", "Clear the custom system prompt"),
        BotCommand("/get_models", "List available AI models and set one if needed"),
        BotCommand("/show_model", "Get model that is currently set"),
        BotCommand("/reset_chat", "Clear chat history and start fresh")
    ])

set_commands()

gemini_api = GeminiAPI(api_key=GEMINI_API_KEY)

# Initialize cache for chat history
chat_history = TTLCache(maxsize=1000, ttl=3600)  # Store 1000 chat histories for 1 hour


@bot.message_handler(commands=['start', 'help'])
@authorized_only(bot, ALLOWED_USERNAMES)
async def handle_start_help(message: Message) -> None:
    await bot.reply_to(message, "Send me a message and I'll try my best to respond!")


@bot.message_handler(commands=['reset_chat'])
@authorized_only(bot, ALLOWED_USERNAMES)
async def handle_reset_chat(message: Message) -> None:
    chat_id = message.chat.id
    if chat_id in chat_history:
        del chat_history[chat_id]
    await bot.reply_to(message, "Chat history has been reset.")

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

@bot.message_handler(commands=['show_model'])
@authorized_only(bot, ALLOWED_USERNAMES)
async def handle_show_model(message: Message) -> None:
    model = model_selector.model
    await bot.reply_to(message, "The current model is: {model}")

@bot.message_handler(commands=['get_models'])
@authorized_only(bot, ALLOWED_USERNAMES)
async def handle_get_models(message: Message) -> None:
    models = model_selector.get_model_list()
    markup = InlineKeyboardMarkup()
    for model in models:
        markup.add(InlineKeyboardButton(model, callback_data=f"set_model:{model}"))
    await bot.reply_to(message, "Here is model selection:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('set_model:'))
async def callback_set_model(call):
    model = call.data.split(':')[1]
    gemini_api.model_selector.model = model
    await bot.answer_callback_query(call.id, f"Model set to {model}")
    await bot.send_message(call.message.chat.id, f"Model has been set to {model}")

@bot.message_handler(func=lambda message: True, content_types=['audio', 'photo', 'document', 'text', 'caption', 'voice'])
@authorized_only(bot, ALLOWED_USERNAMES)
@rate_limit(limit=20, period=60)
async def handle_message(message: Message) -> None:
    chat_id = message.chat.id

    # Handle files first
    if message.content_type in ['audio', 'photo', 'document', 'video', 'voice', 'caption']:
        file_response = await handle_file(message, GEMINI_API_KEY, bot)
        if file_response:
            escaped_file_response = parse_markdown(file_response)
            await bot.reply_to(message, escaped_file_response, parse_mode="HTML")
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
