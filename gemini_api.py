import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import asyncio
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class GeminiAPI:
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro"):
        genai.configure(api_key=api_key)
        self.model_name = model
        self.temperature = 0.7
        self.max_output_tokens = 8192
        self.safety_settings: Dict[HarmCategory, HarmBlockThreshold] = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }

    def _get_model(self):
        return genai.GenerativeModel(model_name=self.model_name)

    async def generate_text(self, prompt: str, system_prompt: str = None) -> str:
        try:
            model = self._get_model(system_prompt)
            response = await asyncio.to_thread(
                model.generate_content,
                prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise

    async def generate_chat(self, messages: List[Dict[str, str]], system_prompt: str = None) -> str:
        try:
            model = self._get_model()
            response = await asyncio.to_thread(
                model.generate_content,
                messages,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_output_tokens,
                ),
                safety_settings=self.safety_settings,
                system_instruction=system_prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating chat response: {e}")
            raise
