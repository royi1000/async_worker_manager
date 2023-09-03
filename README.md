# async_worker_manager

This Python module provides a convenient way to control asyncio parallelism using workers and queues. It allows you to distribute and process tasks asynchronously with a specified number of worker threads while managing potential errors and timeouts.

## Installation

You can install this module using `pip`:

```bash
pip install async_worker_manager
```
Usage
To use this module, follow these steps:

Import the necessary modules:

```python
import asyncio
from async_worker_manager import AsyncWorkerManager
```

Define a function to handle your tasks. This function should take a task as its argument and process it asynchronously.

```python
async def task_handler(task):
    # Your task processing logic here
```
Create an instance of AsyncWorkerManager with your task handler and other optional parameters:
```python
num_workers = 10  # Number of worker threads
queue_size = 100  # Maximum queue size
timeout = 0  # Timeout for each task (0 for no timeout)
timeout_cb = None  # Optional callback function for timed-out tasks

queue = AsyncWorkerManager(task_handler, num_workers=num_workers, queue_size=queue_size, timeout=timeout, timeout_cb=timeout_cb)
```
Start the AsyncWorkerManager:
```python
await queue.start()
```
Add tasks to the queue for processing. You can choose to wait for available space in the queue or not:

```python
task = "Your task data"
await queue.handle(task)  # Add task to the queue (waits if the queue is full)
await queue.handle(task, no_wait=True)  # Add task to the queue (no wait, may raise an exception if the queue is full)
```
Stop the AsyncWorkerManager when you're done:

```python
await queue.stop()
```
Exception Handling:

The task_handler function should handle any exceptions raised during task processing.
You can provide a timeout_cb callback function to handle timed-out tasks.
Example
Here's a complete example:

```python
import asyncio
from asyncio_parallelism_control import AsyncWorkerManager

async def task_handler(task):
    # Simulate task processing
    await asyncio.sleep(1)
    print(f"Processed task: {task}")

async def main():
    num_workers = 5
    queue_size = 10
    timeout = 2

    queue = AsyncWorkerManager(task_handler, num_workers=num_workers, queue_size=queue_size, timeout=timeout)

    await queue.start()

    for i in range(20):
        task = f"Task {i}"
        await queue.handle(task)

    await asyncio.sleep(5)  # Allow time for tasks to complete
    await queue.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

License
This module is open-source and available under the MIT License.
