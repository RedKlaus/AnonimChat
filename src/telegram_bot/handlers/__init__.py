from src.telegram_bot.handlers.communicating import communicating_router
from src.telegram_bot.handlers.user_handlers import user_router

list_handlers = [user_router, communicating_router]

__all__ = ["list_handlers"]
