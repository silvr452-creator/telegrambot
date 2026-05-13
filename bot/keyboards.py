from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.models import ReservationStatus


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Получить информацию")],
            [KeyboardButton(text="Забронировать стол")],
            [KeyboardButton(text="Изменить бронь")],
            [KeyboardButton(text="Отменить бронь")],
            [KeyboardButton(text="Связаться с администратором")],
        ],
        resize_keyboard=True,
    )


def info_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Режим работы"), KeyboardButton(text="Адрес")],
            [KeyboardButton(text="Меню"), KeyboardButton(text="Правила бронирования")],
            [KeyboardButton(text="Акции"), KeyboardButton(text="Контакты")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
    )


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Новые заявки", callback_data="admin:new")
    builder.button(text="Все брони", callback_data="admin:all")
    builder.button(text="Сменить статус", callback_data="admin:status")
    builder.adjust(1)
    return builder.as_markup()


def reservation_actions_keyboard(reservation_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data=f"admin:confirm:{reservation_id}")
    builder.button(text="❌ Отклонить", callback_data=f"admin:reject:{reservation_id}")
    builder.adjust(1)
    return builder.as_markup()


def status_change_keyboard(reservation_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for status in ReservationStatus:
        builder.button(text=status.value, callback_data=f"admin:setstatus:{reservation_id}:{status.value}")
    builder.adjust(2)
    return builder.as_markup()
