def authorized_only(func):
    """Decorator to check if the user is authorized."""

    async def wrapper(message: Message):
        username = message.from_user.username
        if username in ALLOWED_USERNAMES:
            return await func(message)
        else:
            await bot.reply_to(message, "You are not authorized to use this bot.")

    return wrapper
