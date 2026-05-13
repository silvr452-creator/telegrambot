from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards import admin_panel_keyboard, reservation_actions_keyboard, status_change_keyboard
from bot.models import ReservationStatus
from bot.services.reservation_service import ReservationService

router = Router()


def _is_admin(user_id: int, admin_id: int) -> bool:
    return user_id == admin_id


@router.message(F.text == "/admin")
async def admin_panel(message: Message, admin_id: int) -> None:
    if not _is_admin(message.from_user.id, admin_id):
        await message.answer("У вас нет прав администратора.")
        return
    await message.answer("Панель администратора:", reply_markup=admin_panel_keyboard())


@router.callback_query(F.data == "admin:new")
async def admin_new(callback: CallbackQuery, session: AsyncSession, admin_id: int) -> None:
    if not _is_admin(callback.from_user.id, admin_id):
        await callback.answer("Недостаточно прав", show_alert=True)
        return
    service = ReservationService(session)
    items = await service.list_new_reservations()
    if not items:
        await callback.message.answer("Новых заявок нет.")
        await callback.answer()
        return

    for r in items:
        text = f"#{r.id} | {r.client_name} | {r.phone}\n{r.reservation_date} {r.reservation_time} | {r.guests_count} гостей"
        await callback.message.answer(text, reply_markup=reservation_actions_keyboard(r.id))
    await callback.answer()


@router.callback_query(F.data == "admin:all")
async def admin_all(callback: CallbackQuery, session: AsyncSession, admin_id: int) -> None:
    if not _is_admin(callback.from_user.id, admin_id):
        await callback.answer("Недостаточно прав", show_alert=True)
        return
    service = ReservationService(session)
    items = await service.list_all_reservations()
    if not items:
        await callback.message.answer("Брони отсутствуют.")
        await callback.answer()
        return
    lines = ["Все бронирования:"]
    for r in items[:50]:
        lines.append(f"#{r.id}: {r.client_name}, {r.reservation_date} {r.reservation_time}, {r.guests_count}, статус: {r.status}")
    await callback.message.answer("\n".join(lines))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:confirm:"))
async def admin_confirm(callback: CallbackQuery, session: AsyncSession, admin_id: int) -> None:
    await _set_status_from_action(callback, session, admin_id, ReservationStatus.confirmed.value)


@router.callback_query(F.data.startswith("admin:reject:"))
async def admin_reject(callback: CallbackQuery, session: AsyncSession, admin_id: int) -> None:
    await _set_status_from_action(callback, session, admin_id, ReservationStatus.rejected.value)


async def _set_status_from_action(callback: CallbackQuery, session: AsyncSession, admin_id: int, status: str) -> None:
    if not _is_admin(callback.from_user.id, admin_id):
        await callback.answer("Недостаточно прав", show_alert=True)
        return

    reservation_id = int(callback.data.split(":")[-1])
    service = ReservationService(session)
    reservation = await service.get_reservation(reservation_id)
    if not reservation:
        await callback.answer("Бронь не найдена", show_alert=True)
        return

    await service.update_reservation_status(reservation, status)
    await callback.message.answer(f"Статус брони #{reservation.id} обновлен: {status}")
    await callback.answer()


@router.callback_query(F.data == "admin:status")
async def admin_status(callback: CallbackQuery, session: AsyncSession, admin_id: int) -> None:
    if not _is_admin(callback.from_user.id, admin_id):
        await callback.answer("Недостаточно прав", show_alert=True)
        return
    service = ReservationService(session)
    reservations = await service.list_all_reservations()
    for r in reservations[:20]:
        await callback.message.answer(
            f"Бронь #{r.id}, текущий статус: {r.status}",
            reply_markup=status_change_keyboard(r.id),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:setstatus:"))
async def admin_set_status(callback: CallbackQuery, session: AsyncSession, admin_id: int) -> None:
    if not _is_admin(callback.from_user.id, admin_id):
        await callback.answer("Недостаточно прав", show_alert=True)
        return
    _, _, reservation_id, status = callback.data.split(":", maxsplit=3)

    service = ReservationService(session)
    reservation = await service.get_reservation(int(reservation_id))
    if not reservation:
        await callback.answer("Бронь не найдена", show_alert=True)
        return

    await service.update_reservation_status(reservation, status)
    await callback.message.answer(f"Статус брони #{reservation.id} изменен на: {status}")
    await callback.answer()
