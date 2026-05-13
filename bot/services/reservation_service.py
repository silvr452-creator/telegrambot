from datetime import date, time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import FAQ, Reservation, ReservationStatus, User, UserRole


class ReservationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_user(self, telegram_id: int, full_name: str, phone: str | None = None) -> User:
        stmt = select(User).where(User.telegram_id == telegram_id)
        user = (await self.session.execute(stmt)).scalar_one_or_none()
        if user:
            if phone and user.phone != phone:
                user.phone = phone
                await self.session.commit()
            return user

        user = User(telegram_id=telegram_id, full_name=full_name, phone=phone, role=UserRole.client.value)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def create_reservation(
        self,
        user_id: int,
        client_name: str,
        phone: str,
        reservation_date: date,
        reservation_time: time,
        guests_count: int,
        comment: str | None,
    ) -> Reservation:
        reservation = Reservation(
            user_id=user_id,
            client_name=client_name,
            phone=phone,
            reservation_date=reservation_date,
            reservation_time=reservation_time,
            guests_count=guests_count,
            comment=comment,
            status=ReservationStatus.new.value,
        )
        self.session.add(reservation)
        await self.session.commit()
        await self.session.refresh(reservation)
        return reservation

    async def get_faq_by_title(self, title: str) -> FAQ | None:
        return (await self.session.execute(select(FAQ).where(FAQ.title == title))).scalar_one_or_none()

    async def list_reservations_by_phone(self, phone: str) -> list[Reservation]:
        stmt = select(Reservation).where(Reservation.phone == phone).order_by(Reservation.created_at.desc())
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_reservation(self, reservation_id: int) -> Reservation | None:
        return (await self.session.execute(select(Reservation).where(Reservation.id == reservation_id))).scalar_one_or_none()

    async def list_new_reservations(self) -> list[Reservation]:
        stmt = select(Reservation).where(Reservation.status == ReservationStatus.new.value).order_by(Reservation.created_at.asc())
        return list((await self.session.execute(stmt)).scalars().all())

    async def list_all_reservations(self) -> list[Reservation]:
        stmt = select(Reservation).order_by(Reservation.created_at.desc())
        return list((await self.session.execute(stmt)).scalars().all())

    async def update_reservation_fields(
        self,
        reservation: Reservation,
        reservation_date: date,
        reservation_time: time,
        guests_count: int,
    ) -> Reservation:
        reservation.reservation_date = reservation_date
        reservation.reservation_time = reservation_time
        reservation.guests_count = guests_count
        await self.session.commit()
        await self.session.refresh(reservation)
        return reservation

    async def update_reservation_status(self, reservation: Reservation, status: str) -> Reservation:
        reservation.status = status
        await self.session.commit()
        await self.session.refresh(reservation)
        return reservation

    async def seed_initial_faq(self) -> None:
        defaults = {
            "Режим работы": "Пн-Чт: 12:00-00:00, Пт-Сб: 12:00-02:00, Вс: 12:00-23:00",
            "Адрес": "г. Москва, ул. Примерная, 10",
            "Меню": "Авторские коктейли, закуски, горячие блюда и десерты.",
            "Правила бронирования": "Бронь действует 20 минут от указанного времени. Для групп от 8 гостей может потребоваться предоплата.",
        }
        for title, content in defaults.items():
            exists = await self.get_faq_by_title(title)
            if not exists:
                self.session.add(FAQ(title=title, content=content))
        await self.session.commit()
