from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from src.bot.commands.events.text import EventName, EventText
from src.bot.commands.text import Buttons


def get_events_keyboard() -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton(text=EventText.BUTTON_LABELS[name])] for name in EventName]
    buttons.append([KeyboardButton(text=Buttons.CANCEL)])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
