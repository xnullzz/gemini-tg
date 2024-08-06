import logging
import os
import re

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from telegram.helpers import escape_markdown

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from gemini_api import GeminiAPI

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

gemini_api = GeminiAPI(api_key=GEMINI_API_KEY)

def escape_markdown_v2(text, version):
    """
    Custom escape function to handle Telegram's MarkdownV2 while preserving bold syntax.
    """
    if version == 2:
        escape_chars = r'_[]()~`>#+-=|{}.!'
        return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)
    return text

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    response = gemini_api.generate_text(prompt=user_message)

    lines = response.split('\n')
    escaped_lines = []
    for line in lines:
        if line.strip().startswith('*'):  # This is a bullet point
            # Remove the asterisk, add a bullet point, and escape the rest
            escaped_line = '• ' + escape_markdown(line.strip()[1:].strip(), version=2)
        else:
            escaped_line = escape_markdown(line, version=2)
        escaped_lines.append(escaped_line)
    
    escaped_response = '\n'.join(escaped_lines)

    print(escaped_response)

    await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=escaped_response, 
            parse_mode=ParseMode.MARKDOWN_V2)

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm your Gemini-powered bot.")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Help message goes here.")


if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    # Run the bot
    application.run_polling()
