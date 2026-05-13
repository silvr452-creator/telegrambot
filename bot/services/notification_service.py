from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import AdminNotification, Reservation


class NotificationService:
    def __init__(self, session: AsyncSession, bot: Bot, admin_id: int):
        self.session = session
        self.bot = bot
        self.admin_id = admin_id

    async def notify_admin_about_new_reservation(self, reservation: Reservation) -> None:
        text = (
            "📌 Новая заявка на бронь\n"
            f"ID: {reservation.id}\n"
            f"Имя: {reservation.client_name}\n"
            f"Телефон: {reservation.phone}\n"
            f"Дата: {reservation.reservation_date}\n"
            f"Время: {reservation.reservation_time}\n"
            f"Гостей: {reservation.guests_count}\n"
            f"Комментарий: {reservation.comment or '-'}"
        )
        self.session.add(AdminNotification(reservation_id=reservation.id, message=text))
        await self.session.commit()
        await self.bot.send_message(chat_id=self.admin_id, text=text)
