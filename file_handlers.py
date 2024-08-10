import google.generativeai as genai
import asyncio
from telebot.types import Message
from telebot.async_telebot import AsyncTeleBot

async def handle_uploaded_files(bot: AsyncTeleBot, message: Message) -> list:
    """Handles multiple uploaded files and returns a list of genai.File objects."""
    uploaded_files = []

    # Handle photos
    if message.photo:
        for photo in message.photo:
            file_id = photo.file_id
            file_info = await bot.get_file(file_id)
            downloaded_file = await bot.download_file(file_info.file_path)
            uploaded_files.append(genai.upload_file(downloaded_file, mime_type='image/jpeg'))

    # Handle audio
    if message.audio:
        file_id = message.audio.file_id
        file_info = await bot.get_file(file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        uploaded_files.append(genai.upload_file(downloaded_file, mime_type='audio/mpeg'))

    # Handle video
    if message.video:
        file_id = message.video.file_id
        file_info = await bot.get_file(file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        uploaded_files.append(genai.upload_file(downloaded_file, mime_type='video/mp4'))

    # Handle documents (PDF)
    if message.document and message.document.mime_type == 'application/pdf':
        file_id = message.document.file_id
        file_info = await bot.get_file(file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        uploaded_files.append(genai.upload_file(downloaded_file, mime_type='application/pdf'))

    return uploaded_files
