import asyncio
import pytest
from async_worker_manager import AsyncWorkerManager

@pytest.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
async def test_async_queue_basic(event_loop):
    num_workers = 2
    queue_size = 5
    timeout = 2

    log = []

    async def task_handler(task):
        log.append(f"task: {task}")

    queue = AsyncWorkerManager(task_handler, num_workers=num_workers, queue_size=queue_size, timeout=timeout)

    await queue.start()

    for i in range(5):
        task = f"Task {i}"
        await queue.handle(task)

    await asyncio.sleep(5)  # Allow time for tasks to complete
    await queue.stop()
    assert len(log) == 5

@pytest.mark.asyncio
async def test_timeout_handler(event_loop):
    num_workers = 2
    queue_size = 5
    timeout = 0.1

    timeout_log = []

    async def custom_task_handler(task):
            await asyncio.sleep(0.2)  # Simulate a long-running task
            return f"Processed: {task}"

    async def custom_timeout_handler(task):
        timeout_log.append(f"Timeout task: {task}")

    queue = AsyncWorkerManager(custom_task_handler, num_workers=num_workers, 
                               queue_size=queue_size, timeout=timeout, timeout_cb=custom_timeout_handler)

    await queue.start()

    for i in range(5):
        task = f"Task {i}"
        await queue.handle(task)

    await asyncio.sleep(5)  # Allow time for tasks to complete
    await queue.stop()

    # Check if the timeout handler was called for timed-out tasks
    assert len(timeout_log) == 5
