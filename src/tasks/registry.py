import asyncio
from typing import Any

from src.tasks.schemas import Result


class Registry:
    def __init__(self):
        self._pending: dict[str, asyncio.Future[Any]] = {}

    def register(self, task_id: str) -> asyncio.Future[Any]:
        future: asyncio.Future[Any] = asyncio.get_event_loop().create_future()
        self._pending[task_id] = future
        return future

    def resolve(self, result: Result) -> None:
        future = self._pending.pop(result.id, None)
        if future and not future.done():
            future.set_result(result.payload)
