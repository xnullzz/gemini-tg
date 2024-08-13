# model_selector.py

import google.generativeai as genai

class ModelSelector:
    def __init__(self):
        self._model = "gemini-1.5-pro"  # Default model

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    def get_model_list(self):
        model_list = []
        for model in genai.list_models():
            if "generateContent" in model.supported_generation_methods:
                # Remove the "models/" prefix
                model_name = model.name.replace("models/", "")
                model_list.append(model_name)
        return model_list
