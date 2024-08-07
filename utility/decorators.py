from telebot.types import Message

def authorized_only(allowed_usernames):
    """Decorator to check if the user is authorized."""

    def decorator(func):
        async def wrapper(message: Message):
            username = message.from_user.username
            if username in allowed_usernames:
                return await func(message)
            else:
                # Access the bot instance from the decorated function
                bot = func.__self__  
                await bot.reply_to(message, "You are not authorized to use this bot.")
        return wrapper
    return decorator
