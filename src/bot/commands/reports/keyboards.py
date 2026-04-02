from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from src.bot.commands.reports.text import ReportName, ReportText
from src.bot.commands.text import Buttons


def get_reports_keyboard() -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton(text=ReportText.BUTTON_LABELS[name])] for name in ReportName]
    buttons.append([KeyboardButton(text=Buttons.CANCEL)])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
