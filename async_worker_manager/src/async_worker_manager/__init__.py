import asyncio
from enum import Enum
import logging

Status = Enum('Status', 'init started stopped')

logger = logging.getLogger('async_worker_manager')
logger.setLevel(logging.INFO)


async def worker(name, queue, handler, timeout=0, timeout_cb=None):
    while True:
        task = await queue.get()
        try:
            if timeout:
                await asyncio.wait_for(handler(task), timeout=timeout)
            else:
                await handler(task)
        except asyncio.TimeoutError:
            logger.warning(f"{name}: Timeout processing message: {task}")
            if timeout_cb:
                try:
                    await timeout_cb(task)
                except Exception as e:
                    logger.warning(f"{name}: Error on timeout callback: {task}")
        except Exception as e:
            logger.exception(f"{name}: Error processing message: {e}")
        finally:
            queue.task_done()


class AsyncWorkerManager:
    def __init__(self, handler, num_workers: int=10, queue_size:int=100, timeout=0, timeout_cb=None) -> None:
        self.handler = handler
        self.num_workers: int = num_workers
        self.timeout = timeout
        self.timeout_cb = timeout_cb
        self.queue = None
        self.queue_size: int = queue_size
        self.workers: list = None
        self.status: str = Status.init

    async def start(self) -> None:
        if self.status != Status.init:
            raise ValueError(f'status: {self.status} is not {Status.init}')
        self.queue = asyncio.Queue(maxsize=self.queue_size)
        self.workers = [asyncio.create_task(worker('worker-{i}', 
                            self.queue, self.handler, self.timeout, self.timeout_cb)) for i in range(self.num_workers)]
        self.status = Status.started

    async def stop(self) -> None:
        if self.status != Status.started:
            return
        await self.queue.join()
        for work in self.workers:
            work.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.status = Status.stopped

    async def handle(self, task, no_wait=False) -> None:
        if no_wait:
            await self.queue.put_nowait(task)
        else:
            await self.queue.put(task)
        