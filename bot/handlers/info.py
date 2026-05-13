from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards import info_menu_keyboard, main_menu_keyboard
from bot.services.reservation_service import ReservationService

router = Router()


@router.message(F.text == "Получить информацию")
async def info_menu(message: Message) -> None:
    await message.answer("Выберите раздел со справочной информацией:", reply_markup=info_menu_keyboard())


@router.message(F.text == "⬅️ Назад")
async def back_to_menu(message: Message) -> None:
    await message.answer("Главное меню", reply_markup=main_menu_keyboard())


@router.message(F.text.in_({"Режим работы", "Адрес", "Меню", "Правила бронирования", "Акции", "Контакты"}))
async def info_item(message: Message, session: AsyncSession) -> None:
    static_items = {
        "Акции": "Сегодня: 2+1 на безалкогольные коктейли до 18:00.",
        "Контакты": "+7 (900) 000-00-00, @bar_support",
    }
    if message.text in static_items:
        await message.answer(static_items[message.text])
        return

    service = ReservationService(session)
    faq = await service.get_faq_by_title(message.text)
    if not faq:
        await message.answer("Информация пока недоступна.")
        return
    await message.answer(f"{faq.title}:\n{faq.content}")
