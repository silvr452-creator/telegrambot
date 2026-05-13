import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware, Bot, Dispatcher
from aiogram.types import TelegramObject

from bot.config import Config, load_config
from bot.database import Database
from bot.handlers import admin, booking, info, user
from bot.services.notification_service import NotificationService
from bot.services.reservation_service import ReservationService


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, database: Database):
        self.database = database

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async for session in self.database.get_session():
            data["session"] = session
            return await handler(event, data)


class AppContextMiddleware(BaseMiddleware):
    def __init__(self, config: Config, bot: Bot):
        self.config = config
        self.bot = bot

    async def __call__(self, handler, event, data):
        data["admin_id"] = self.config.admin_id
        data["notification_service_factory"] = (
            lambda session: NotificationService(session=session, bot=self.bot, admin_id=self.config.admin_id)
        )
        return await handler(event, data)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    config = load_config()
    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    db = Database(config.database_url)

    dp.update.middleware(DbSessionMiddleware(db))
    dp.update.middleware(AppContextMiddleware(config, bot))

    dp.include_router(user.router)
    dp.include_router(info.router)
    dp.include_router(booking.router)
    dp.include_router(admin.router)

    # Добавляем базовые FAQ при первом запуске.
    async for session in db.get_session():
        await ReservationService(session).seed_initial_faq()
        break

    try:
        await dp.start_polling(bot)
    finally:
        await db.dispose()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped")
