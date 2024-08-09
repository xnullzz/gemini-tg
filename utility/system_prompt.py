class SystemPromptManager:
    def __init__(self):
        self.prompts = {}

    def set_prompt(self, chat_id: int, prompt: str) -> None:
        """Sets or updates the system prompt for a given chat."""
        self.prompts[chat_id] = prompt

    def get_prompt(self, chat_id: int) -> str:
        """Retrieves the system prompt for a given chat. Returns a default prompt if none is set."""
        return self.prompts.get(chat_id, " ")

    def clear_prompt(self, chat_id: int) -> None:
        """Resets the system prompt for a given chat to the default."""
        if chat_id in self.prompts:
            del self.prompts[chat_id]
