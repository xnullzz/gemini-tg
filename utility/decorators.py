from telebot.types import Message
import time
from functools import wraps
from cachetools import TTLCache

def authorized_only(bot, allowed_usernames):
    """Decorator to check if the user is authorized."""
    def decorator(func):
        @wraps(func)
        async def wrapper(message: Message, *args, **kwargs):
            username = message.from_user.username
            if username in allowed_usernames:
                return await func(message, *args, **kwargs)
            else:
                await bot.reply_to(message, "You are not authorized to use this bot.")
        return wrapper
    return decorator

def rate_limit(limit: int, period: int):
    """Decorator to implement rate limiting."""
    cache = TTLCache(maxsize=10000, ttl=period)

    def decorator(func):
        @wraps(func)
        async def wrapper(message: Message, *args, **kwargs):
            user_id = message.from_user.id
            current_time = time.time()

            if user_id in cache:
                timestamps = cache[user_id]
                timestamps = [t for t in timestamps if current_time - t < period]

                if len(timestamps) >= limit:
                    await message.reply("Rate limit exceeded. Please try again later.")
                    return

                timestamps.append(current_time)
                cache[user_id] = timestamps
            else:
                cache[user_id] = [current_time]

            return await func(message, *args, **kwargs)
        return wrapper
    return decorator
