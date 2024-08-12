import google.generativeai as genai
from telebot.types import Message
import time
import mimetypes
import os

async def handle_file(message: Message, gemini_api_key: str, bot) -> str:
    """Retrieves a file from the message and sends it to Gemini for analysis."""
    file_id = None
    file_type = None
    file_ext = None
    mimetypes.add_type("audio/ogg", ".ogg")

    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = 'image'
        file_ext = '.jpg'
    elif message.audio:
        file_id = message.audio.file_id
        file_type = 'audio'
        file_ext = '.' + (message.audio.mime_type.split('/')[-1] if message.audio.mime_type else 'mp3')
    elif message.voice:
        file_id = message.voice.file_id
        file_type = 'voice'
        file_ext = '.ogg'
    elif message.document:
        file_id = message.document.file_id
        file_type = 'document'
        file_ext = os.path.splitext(message.document.file_name)[1] if message.document.file_name else ''
    elif message.video:
        file_id = message.video.file_id
        file_type = 'video'
        file_ext = '.mp4'

    if not file_id:
        return None

    try:
        file_info = await bot.get_file(file_id)
        file_content = await bot.download_file(file_info.file_path)

        genai.configure(api_key=gemini_api_key)
        system_instruction = (
                "You are an AI assistant capable of analyzing various types of files. "
                "You have been provided with a file to analyze. "
                "Always assume you can access and understand the contents of the file. "
                "Respond to the user's query about the file based on your analysis. "
                "If no specific query is provided, give a general description or summary of the file's contents."
            )
        model = genai.GenerativeModel("gemini-1.5-pro", system_instruction=system_instruction)

        # Create a temporary file with the correct extension
        temp_filename = f'temp_file{file_ext}'
        with open(temp_filename, 'wb') as temp_file:
            temp_file.write(file_content)
        
        # Get the correct MIME type
        mime_type, _ = mimetypes.guess_type(temp_filename)
        if not mime_type:
            mime_type = 'application/octet-stream'

        uploaded_file = genai.upload_file(temp_filename, mime_type=mime_type)

        # For video files, wait for processing
        if file_type == 'video':
            while uploaded_file.state.name == "PROCESSING":
                print("Processing video...")
                time.sleep(5)
                uploaded_file = genai.get_file(uploaded_file.name)

        prompt = message.caption or get_default_prompt(file_type)
        print(f"DEBUG: Using prompt: {prompt}")

        response = model.generate_content([uploaded_file, prompt])
        
        # Clean up the temporary file
        os.remove(temp_filename)

        return response.text

    except Exception as e:
        print(f"Error handling file: {e}")
        return f"An error occurred while processing the file: {str(e)}"

def get_default_prompt(file_type: str) -> str:
    """Returns a default prompt based on the file type."""
    prompts = {
        'image': "Describe this image in detail, including objects, people, and background.",
        'audio': "Describe this audio clip and summarize its content.",
        'document': "Summarize this document and identify any key topics or themes.",
        'video': "Describe this video clip in detail.",
        'voice': "You've given a voice message of a user. Please reply to the user in the language user is talking to you in this message"
    }
    return prompts.get(file_type, "Analyze this file and provide a summary of its contents.")
