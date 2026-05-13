from datetime import date, datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards import main_menu_keyboard
from bot.services.notification_service import NotificationService
from bot.services.reservation_service import ReservationService
from bot.states import BookingStates, CancelReservationStates, UpdateReservationStates

router = Router()


def _is_valid_phone(phone: str) -> bool:
    digits = "".join(ch for ch in phone if ch.isdigit())
    return 10 <= len(digits) <= 15


@router.message(F.text == "Забронировать стол")
async def start_booking(message: Message, state: FSMContext) -> None:
    await state.set_state(BookingStates.waiting_name)
    await message.answer("Введите имя клиента:")


@router.message(BookingStates.waiting_name)
async def booking_name(message: Message, state: FSMContext) -> None:
    await state.update_data(client_name=message.text.strip())
    await state.set_state(BookingStates.waiting_phone)
    await message.answer("Введите номер телефона:")


@router.message(BookingStates.waiting_phone)
async def booking_phone(message: Message, state: FSMContext) -> None:
    if not _is_valid_phone(message.text):
        await message.answer("Некорректный телефон. Попробуйте снова.")
        return
    await state.update_data(phone=message.text.strip())
    await state.set_state(BookingStates.waiting_date)
    await message.answer("Введите дату бронирования в формате ГГГГ-ММ-ДД:")


@router.message(BookingStates.waiting_date)
async def booking_date(message: Message, state: FSMContext) -> None:
    try:
        reservation_date = datetime.strptime(message.text.strip(), "%Y-%m-%d").date()
    except ValueError:
        await message.answer("Некорректная дата. Используйте формат ГГГГ-ММ-ДД.")
        return

    if reservation_date < date.today():
        await message.answer("Нельзя создать бронь на прошедшую дату.")
        return

    await state.update_data(reservation_date=reservation_date.isoformat())
    await state.set_state(BookingStates.waiting_time)
    await message.answer("Введите время в формате ЧЧ:ММ:")


@router.message(BookingStates.waiting_time)
async def booking_time(message: Message, state: FSMContext) -> None:
    try:
        reservation_time = datetime.strptime(message.text.strip(), "%H:%M").time()
    except ValueError:
        await message.answer("Некорректное время. Используйте формат ЧЧ:ММ.")
        return
    await state.update_data(reservation_time=reservation_time.isoformat())
    await state.set_state(BookingStates.waiting_guests)
    await message.answer("Введите количество гостей (1-20):")


@router.message(BookingStates.waiting_guests)
async def booking_guests(message: Message, state: FSMContext) -> None:
    if not message.text.isdigit() or not 1 <= int(message.text) <= 20:
        await message.answer("Количество гостей должно быть от 1 до 20.")
        return
    await state.update_data(guests_count=int(message.text))
    await state.set_state(BookingStates.waiting_comment)
    await message.answer("Комментарий к брони (или '-' если без комментария):")


@router.message(BookingStates.waiting_comment)
async def booking_comment(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    notification_service_factory,
) -> None:
    data = await state.get_data()
    comment = message.text.strip()
    comment = None if comment == "-" else comment

    service = ReservationService(session)
    user = await service.get_or_create_user(
        telegram_id=message.from_user.id,
        full_name=message.from_user.full_name,
        phone=data["phone"],
    )
    reservation = await service.create_reservation(
        user_id=user.id,
        client_name=data["client_name"],
        phone=data["phone"],
        reservation_date=datetime.fromisoformat(data["reservation_date"]).date(),
        reservation_time=datetime.fromisoformat(f"2000-01-01T{data['reservation_time']}").time(),
        guests_count=data["guests_count"],
        comment=comment,
    )

    notifier: NotificationService = notification_service_factory(session)
    await notifier.notify_admin_about_new_reservation(reservation)

    await message.answer(
        f"Спасибо! Заявка №{reservation.id} принята со статусом '{reservation.status}'.",
        reply_markup=main_menu_keyboard(),
    )
    await state.clear()


@router.message(F.text == "Изменить бронь")
async def update_start(message: Message, state: FSMContext) -> None:
    await state.set_state(UpdateReservationStates.waiting_phone)
    await message.answer("Введите номер телефона, который указывали при бронировании:")


@router.message(UpdateReservationStates.waiting_phone)
async def update_phone(message: Message, state: FSMContext, session: AsyncSession) -> None:
    service = ReservationService(session)
    reservations = await service.list_reservations_by_phone(message.text.strip())
    if not reservations:
        await message.answer("Брони не найдены.", reply_markup=main_menu_keyboard())
        await state.clear()
        return
    lines = ["Найдены брони. Введите ID нужной брони:"]
    for r in reservations:
        lines.append(f"ID {r.id}: {r.reservation_date} {r.reservation_time} ({r.guests_count} гостей), статус: {r.status}")
    await state.update_data(phone=message.text.strip())
    await state.set_state(UpdateReservationStates.waiting_reservation_id)
    await message.answer("\n".join(lines))


@router.message(UpdateReservationStates.waiting_reservation_id)
async def update_pick_reservation(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not message.text.isdigit():
        await message.answer("Введите корректный ID брони.")
        return
    service = ReservationService(session)
    reservation = await service.get_reservation(int(message.text))
    if not reservation:
        await message.answer("Бронь не найдена.")
        return
    await state.update_data(reservation_id=reservation.id)
    await state.set_state(UpdateReservationStates.waiting_new_date)
    await message.answer("Введите новую дату (ГГГГ-ММ-ДД):")


@router.message(UpdateReservationStates.waiting_new_date)
async def update_new_date(message: Message, state: FSMContext) -> None:
    try:
        dt = datetime.strptime(message.text.strip(), "%Y-%m-%d").date()
    except ValueError:
        await message.answer("Некорректная дата.")
        return
    if dt < date.today():
        await message.answer("Дата не может быть в прошлом.")
        return
    await state.update_data(new_date=dt.isoformat())
    await state.set_state(UpdateReservationStates.waiting_new_time)
    await message.answer("Введите новое время (ЧЧ:ММ):")


@router.message(UpdateReservationStates.waiting_new_time)
async def update_new_time(message: Message, state: FSMContext) -> None:
    try:
        tm = datetime.strptime(message.text.strip(), "%H:%M").time()
    except ValueError:
        await message.answer("Некорректное время.")
        return
    await state.update_data(new_time=tm.isoformat())
    await state.set_state(UpdateReservationStates.waiting_new_guests)
    await message.answer("Введите новое количество гостей (1-20):")


@router.message(UpdateReservationStates.waiting_new_guests)
async def update_new_guests(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not message.text.isdigit() or not 1 <= int(message.text) <= 20:
        await message.answer("Количество гостей должно быть от 1 до 20.")
        return

    data = await state.get_data()
    service = ReservationService(session)
    reservation = await service.get_reservation(int(data["reservation_id"]))
    if not reservation:
        await message.answer("Бронь не найдена.")
        await state.clear()
        return

    await service.update_reservation_fields(
        reservation,
        reservation_date=datetime.fromisoformat(data["new_date"]).date(),
        reservation_time=datetime.fromisoformat(f"2000-01-01T{data['new_time']}").time(),
        guests_count=int(message.text),
    )
    await message.answer("Бронь успешно обновлена.", reply_markup=main_menu_keyboard())
    await state.clear()


@router.message(F.text == "Отменить бронь")
async def cancel_start(message: Message, state: FSMContext) -> None:
    await state.set_state(CancelReservationStates.waiting_phone)
    await message.answer("Введите номер телефона для поиска брони:")


@router.message(CancelReservationStates.waiting_phone)
async def cancel_phone(message: Message, state: FSMContext, session: AsyncSession) -> None:
    service = ReservationService(session)
    reservations = await service.list_reservations_by_phone(message.text.strip())
    if not reservations:
        await message.answer("Брони не найдены.", reply_markup=main_menu_keyboard())
        await state.clear()
        return
    lines = ["Введите ID брони для отмены:"]
    for r in reservations:
        lines.append(f"ID {r.id}: {r.reservation_date} {r.reservation_time}, статус: {r.status}")
    await state.set_state(CancelReservationStates.waiting_reservation_id)
    await message.answer("\n".join(lines))


@router.message(CancelReservationStates.waiting_reservation_id)
async def cancel_confirm(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not message.text.isdigit():
        await message.answer("Введите корректный ID.")
        return
    service = ReservationService(session)
    reservation = await service.get_reservation(int(message.text))
    if not reservation:
        await message.answer("Бронь не найдена.")
        return
    await service.update_reservation_status(reservation, "Отменена")
    await message.answer("Бронь отменена.", reply_markup=main_menu_keyboard())
    await state.clear()
