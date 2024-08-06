import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import asyncio

class GeminiAPI:
    def __init__(self, api_key, model="gemini-1.5-pro"):
        genai.configure(api_key=api_key)
        self.model = model
        self.temperature = 0.7
        self.max_output_tokens = 8192
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }

    async def generate_text(self, prompt):
        loop = asyncio.get_event_loop()
        model_selected = genai.GenerativeModel(self.model)
        response = await loop.run_in_executor(
            None,
            lambda: model_selected.generate_content(prompt, safety_settings=self.safety_settings)
        )
        return response.text
