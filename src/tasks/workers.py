import uuid
from abc import ABC, abstractmethod
from typing import Any

from src.config import settings
from src.queue import RabbitMQConnection, RabbitMQProducer
from src.tasks.registry import Registry
from src.tasks.schemas import Result, ScheduleTask, Task


class Worker(ABC):
    def __init__(self, connection: RabbitMQConnection, registry: Registry):
        self.connection = connection
        self.producer = RabbitMQProducer(self.connection)
        self.registry = registry

    @abstractmethod
    def _construct_task(self, **params: Any) -> Task: ...

    def _create_id(self) -> str:
        return str(uuid.uuid4())

    def _return_result(self, result: Result) -> dict[str, Any]:
        return result.payload

    async def run(self, **params: Any) -> dict[str, Any]:
        task = self._construct_task(**params)
        future = self.registry.register(task.id)

        await self.producer.send_message(
            exchange_name=settings.EXCHANGE_NAME,
            routing_key=f"{settings.QUEUE_ORACLE}.{settings.RK_REQUEST}",
            message=task.model_dump(),
        )

        return await future


class ScheduleWorker(Worker):
    def _construct_task(self, **params: Any) -> Task:
        task = ScheduleTask(id=self._create_id(), payload=dict(params))

        return task
