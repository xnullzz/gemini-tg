import google.generativeai as genai
from telebot.types import Message
import io

async def handle_file(message: Message, gemini_api_key: str, bot) -> str:
    """Retrieves a file from the message and sends it to Gemini for analysis."""
    file_id = None
    file_type = None
    mime_type = None

    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = 'image'
        mime_type = 'image/jpeg'
    elif message.audio:
        file_id = message.audio.file_id
        file_type = 'audio'
        mime_type = message.audio.mime_type
    elif message.document:
        file_id = message.document.file_id
        file_type = 'document'
        mime_type = message.document.mime_type

    if not file_id:
        return None

    try:
        file_info = await bot.get_file(file_id)
        file_content = await bot.download_file(file_info.file_path)

        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-pro")

        prompt = message.caption or get_default_prompt(file_type)
        print(f"DEBUG: Using prompt: {prompt}")

        # Create a file-like object from bytes
        file_obj = io.BytesIO(file_content)
        file_obj.name = f"file.{mime_type.split('/')[-1]}"  # Set a filename

        response = model.generate_content([file_obj, prompt])
        return response.text

    except Exception as e:
        print(f"Error handling file: {e}")
        return f"An error occurred while processing the file: {str(e)}"

def get_default_prompt(file_type: str) -> str:
    """Returns a default prompt based on the file type."""
    prompts = {
        'image': "Describe this image in detail, including objects, people, and background.",
        'audio': "Transcribe this audio clip and summarize its content.",
        'document': "Summarize this document and identify any key topics or themes."
    }
    return prompts.get(file_type, "Analyze this file and provide a summary of its contents.")
