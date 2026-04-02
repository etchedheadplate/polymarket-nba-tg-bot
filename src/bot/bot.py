from aiogram import Bot, Dispatcher

from src.bot.commands.events import schedule_router
from src.bot.commands.reports import reports_router
from src.bot.commands.start import start_router
from src.bot.commands.update import update_router


async def create_bot(token: str):
    bot = Bot(token=token)
    dp = Dispatcher()

    dp.include_router(schedule_router)
    dp.include_router(start_router)
    dp.include_router(update_router)
    dp.include_router(reports_router)

    return bot, dp
