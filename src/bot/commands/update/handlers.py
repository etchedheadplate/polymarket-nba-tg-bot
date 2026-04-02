from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.queue import RabbitMQConnection
from src.tasks import Registry, UpdateWorker

router = Router()


@router.message(Command("update"))
async def update_command_handler(message: Message, connection: RabbitMQConnection, registry: Registry):
    await message.answer("Started database update")
    worker = UpdateWorker(connection=connection, registry=registry)
    payload = await worker.run()
    text_response: list[str] = [f"Database updated in {payload['time']} seconds\n"]
    for name, counts in payload["tables"].items():
        table_line = f"{name.capitalize()}: updated {counts['updated']} of which new {counts['new']}"
        text_response.append(table_line)
    formatted_text = f"```\n{'\n'.join(text_response)}```"
    await message.answer(formatted_text, parse_mode="MarkdownV2")
