import asyncio
from typing import Any

from src.bot.bot import create_bot
from src.config import settings
from src.queue.connection import RabbitMQConnection
from src.queue.consumer import RabbitMQConsumer
from src.queue.producer import RabbitMQProducer


async def main():
    connection = RabbitMQConnection()
    consumer = RabbitMQConsumer(connection, service_name=settings.SERVICE_NAME)
    producer = RabbitMQProducer(connection)

    bot, dp = await create_bot(settings.TG_BOT_TOKEN)

    consumer_task: asyncio.Task[Any] | None = None

    async def handle_message(msg: dict[str, Any]):
        result: dict[str, Any] = {"status": "received"}
        await producer.send_message(
            settings.EXCHANGE_NAME,
            settings.RK_ORACLE_QUERY,
            result,
        )

    @dp.startup()
    async def on_startup(**kwargs: Any) -> None:  # pyright: ignore[reportUnusedFunction]
        nonlocal consumer_task
        consumer_task = asyncio.create_task(
            consumer.consume(
                settings.EXCHANGE_NAME,
                settings.RK_ORACLE_RESPONSE,
                handle_message,
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
