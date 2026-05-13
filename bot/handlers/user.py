from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Добро пожаловать в бот бронирования бара! Выберите действие в меню ниже.",
        reply_markup=main_menu_keyboard(),
    )


@router.message(lambda m: m.text == "Связаться с администратором")
async def contact_admin(message: Message) -> None:
    await message.answer("Напишите ваш вопрос в этот чат, и администратор свяжется с вами.")
