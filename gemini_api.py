import google.generativeai as genai

class GeminiAPI:
    def __init__(self, api_key, model="gemini-1.5-pro"):  # Replace ::MODEL_NAME:: with the actual model name
        genai.configure(api_key=api_key)
        self.model = model

    def generate_text(self, prompt):
        model_selected = genai.GenerativeModel(self.model)
        response = model_selected.generate_content(prompt)
        return response.result
