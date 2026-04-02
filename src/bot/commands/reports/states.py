from aiogram.fsm.state import State, StatesGroup


class ReportForm(StatesGroup):
    report_name = State()
    team = State()
    team_side = State()
    team_vs = State()
