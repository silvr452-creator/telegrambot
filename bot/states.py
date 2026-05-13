from aiogram.fsm.state import State, StatesGroup


class BookingStates(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_date = State()
    waiting_time = State()
    waiting_guests = State()
    waiting_comment = State()


class UpdateReservationStates(StatesGroup):
    waiting_phone = State()
    waiting_reservation_id = State()
    waiting_new_date = State()
    waiting_new_time = State()
    waiting_new_guests = State()


class CancelReservationStates(StatesGroup):
    waiting_phone = State()
    waiting_reservation_id = State()
