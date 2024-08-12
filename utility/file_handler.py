import google.generativeai as genai
from telebot.types import Message
import time

async def handle_file(message: Message, gemini_api_key: str, bot) -> str:
    """Retrieves a file from the message and sends it to Gemini for analysis."""
    file_id = None
    file_type = None

    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = 'image'
    elif message.audio or message.voice:
        file_id = message.audio.file_id if message.audio else message.voice.file_id
        file_type = 'audio'
    elif message.document:
        file_id = message.document.file_id
        file_type = 'document'
    elif message.video:
        file_id = message.video.file_id
        file_type = 'video'

    if not file_id:
        return None

    try:
        file_info = await bot.get_file(file_id)
        file_content = await bot.download_file(file_info.file_path)

        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-pro")

        # Create a temporary file and upload it
        with open('temp_file', 'wb') as temp_file:
            temp_file.write(file_content)
        
        uploaded_file = genai.upload_file('temp_file')

        # For video files, wait for processing
        if file_type == 'video':
            while uploaded_file.state.name == "PROCESSING":
                print("Processing video...")
                time.sleep(5)
                uploaded_file = genai.get_file(uploaded_file.name)

        prompt = message.caption or get_default_prompt(file_type)
        print(f"DEBUG: Using prompt: {prompt}")

        response = model.generate_content([uploaded_file, prompt])
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
        'video': "Describe this video clip in detail."
    }
    return prompts.get(file_type, "Analyze this file and provide a summary of its contents.")
