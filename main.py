import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from src.config import settings

TOKEN = settings.TG_BOT_TOKEN


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start_handler(message: Message):  # pyright: ignore[reportUnusedFunction]
        await message.answer("Hello!")

    await dp.start_polling(bot)  # pyright: ignore[reportUnknownMemberType]


if __name__ == "__main__":
    asyncio.run(main())
