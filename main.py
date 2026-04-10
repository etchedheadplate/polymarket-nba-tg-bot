import asyncio
from typing import Any

from src.bot.bot import create_bot
from src.config import settings
from src.queue import RabbitMQConnection, RabbitMQConsumer
from src.tasks import Registry, Result


async def main():
    connection = RabbitMQConnection()
    consumer = RabbitMQConsumer(connection)
    registry = Registry()

    bot, dp = await create_bot(settings.TG_BOT_TOKEN)

    consumer_task: asyncio.Task[Any] | None = None

    async def handle_message(msg: dict[str, Any]) -> None:
        result = Result(**msg)
        registry.resolve(result)

    @dp.startup()
    async def on_startup(**kwargs: Any) -> None:  # pyright: ignore[reportUnusedFunction]
        nonlocal consumer_task
        dp["connection"] = connection
        dp["registry"] = registry

        consumer_task = asyncio.create_task(
            consumer.consume(
                exchange_name=settings.EXCHANGE_NAME,
                routing_key=f"{settings.QUEUE_TG_BOT}.{settings.RK_RESPONSE}",
                callback=handle_message,
            )
        )

    @dp.shutdown()
    async def on_shutdown(**kwargs: Any) -> None:  # pyright: ignore[reportUnusedFunction]
        if consumer_task:
            consumer_task.cancel()
            await asyncio.gather(consumer_task, return_exceptions=True)
        await connection.close()
        await bot.session.close()

    await dp.start_polling(bot)  # pyright: ignore[reportUnknownMemberType]


if __name__ == "__main__":
    asyncio.run(main())
