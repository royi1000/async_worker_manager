import asyncio
import logging

INIT='init'
STARTED='started'
STOPPED = 'stopped'

logger = logging.getLogger('asyncqueue')

async def worker(name, queue, handler, timeout=0, timeout_cb=None):
    while True:
        task = await queue.get()
        try:
            if timeout:
                await asyncio.wait_for(handler(task), timeout=timeout)
            else:
                await handler(task)
        except asyncio.TimeoutError:
            logging.warning(f"{name}: Timeout processing message: {task}")
            if timeout_cb:
                try:
                    timeout_cb(task)
                except Exception as e:
                    logging.warning(f"{name}: Error on timeout callback: {task}")
        except Exception as e:
            logging.warning(f"{name}: Error processing message: {e}")
        finally:
            queue.task_done()



class AsyncQueue:
    def __init__(self, handler, num_workers: int=10, queue_size:int=100, timeout=0, timeout_cb=None) -> None:
        self.handler = handler
        self.num_workers: int = num_workers
        self.timeout = timeout
        self.timeout_cb = timeout_cb
        self.queue = None
        self.queue_size: int = queue_size
        self.workers: list = None
        self.status: str = INIT
    
    async def start(self) -> None:
        if self.status != INIT:
            raise ValueError(f'status: {self.status} is not {INIT}')
        queue = asyncio.Queue(maxsize=self.queue_size)
        tasks = [asyncio.create_task(worker('worker-{i}', queue, self.timeout, self.timeout_cb)) for i in range(num_workers)]
        self.status = STARTED

    async def stop(self) -> None:
        if self.status != STARTED:
            return
        await queue.join()
        for work in self.workers:
            work.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.status = STOPPED

    async def handle(self, task, no_wait=False) -> None:
        if no_wait:
            await self.queue.put_nowait(task)
        else:
            await self.queue.put(task)
        