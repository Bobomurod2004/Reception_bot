from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    """User FSM holatlar"""
    choosing_category = State()
    writing_message = State()
    waiting_response = State()


class AdminStates(StatesGroup):
    """Admin FSM holatlar"""
    choosing_ticket = State()
    replying = State()
    replying_ticket_id = State()  # Javob berilayotgan ticket ID
    closing_ticket = State()
    writing_close_reason = State()
    close_reason_ticket_id = State()  # Yopilayotgan ticket ID
    picking_date = State()


class SuperAdminStates(StatesGroup):
    """Super Admin FSM holatlar"""
    managing_admins = State()
    managing_categories = State()
    viewing_reports = State()
    creating_admin = State()
    creating_category = State()
