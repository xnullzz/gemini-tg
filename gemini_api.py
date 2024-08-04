import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

class GeminiAPI:
    def __init__(self, api_key, model="gemini-1.5-pro"):  # Replace ::MODEL_NAME:: with the actual model name
        genai.configure(api_key=api_key)
        self.model = model
        self.temperature = 0.7
        self.max_output_tokens = 8192
        #Установить BLOCK_NONE, если появится такая возможность
        self.safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            }


    def generate_text(self, prompt):
        model_selected = genai.GenerativeModel(self.model)
        response = model_selected.generate_content(prompt, safety_settings=self.safety_settings)
        return response.test
