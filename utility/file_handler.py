import google.generativeai as genai
from telebot.types import Message

def handle_file(message: Message, gemini_api_key: str, bot) -> str:  # Add bot as a parameter
    """Retrieves a file from the message and sends it to Gemini for analysis.

    Args:
        message: The Telegram message object.
        gemini_api_key: The API key for Google Gemini.
        bot: The telebot instance.  # Add this line

    Returns:
        The response from Gemini, or None if no file was found.
    """
    file_id = None
    file_type = None

    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = 'image'
    elif message.audio:
        file_id = message.audio.file_id
        file_type = 'audio'
    elif message.document:
        file_id = message.document.file_id
        file_type = 'document'

    if file_id:
        try:
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            genai.configure(api_key=gemini_api_key)
            uploaded_file = genai.upload_file(media / downloaded_file)

            model = genai.GenerativeModel("gemini-1.5-pro")  # Use gemini-1.5-pro

            # Use caption as prompt if it exists
            if message.caption:
                prompt = message.caption
                print(f"DEBUG: Using caption as prompt: {prompt}")
            elif file_type == 'image':
                prompt = "Describe this image in detail, including objects, people, and background."
            elif file_type == 'audio':
                prompt = "Transcribe this audio clip and summarize its content."
            else:
                prompt = "Summarize this document and identify any key topics or themes."

            print(f"DEBUG: Sending prompt to Gemini: {prompt}")

            result = model.generate_content([uploaded_file, prompt])
            return result.text

        except Exception as e:
            print(f"Error handling file: {e}")
            return None

    return None
