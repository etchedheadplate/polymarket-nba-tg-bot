from typing import Any

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from src.bot.commands.text import Buttons
from src.bot.domain import NBATeam, NBATeamSide


def get_return_keyboard() -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton(text=Buttons.CANCEL), KeyboardButton(text=Buttons.BACK)]]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def _chunk(items: list[Any], size: int) -> list[list[Any]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def get_teams_keyboard(optional: bool = False, back: bool = True) -> ReplyKeyboardMarkup:
    team_buttons = [KeyboardButton(text=team.name) for team in NBATeam]
    rows = _chunk(team_buttons, 5)
    if optional:
        rows.append([KeyboardButton(text=Buttons.ALL_TEAMS)])
    nav = []
    if back:
        nav.append(KeyboardButton(text=Buttons.BACK))  # pyright: ignore[reportUnknownMemberType]
    nav.append(KeyboardButton(text=Buttons.BACK))  # pyright: ignore[reportUnknownMemberType]
    rows.append(nav)  # pyright: ignore[reportUnknownArgumentType]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def get_team_side_keyboard() -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton(text=side.value.capitalize())] for side in NBATeamSide]
    buttons.append([KeyboardButton(text=Buttons.ANY_SIDE)])
    buttons.append([KeyboardButton(text=Buttons.CANCEL), KeyboardButton(text=Buttons.BACK)])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
