from aiogram.fsm.state import State, StatesGroup


class EventsForm(StatesGroup):
    event_name = State()
    start_date = State()
    end_date = State()
    team = State()
    team_side = State()
    team_vs = State()
