import asyncio
from typing import Any, Callable, TypeVar

T = TypeVar("T")


async def run_async(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """
    Run a synchronous function asynchronously in a separate thread.

    Parameters:
    - func: The synchronous function to be executed.
    - *args: Positional arguments to be passed to the function.
    - **kwargs: Keyword arguments to be passed to the function.

    Returns:
    - The result of the synchronous function.

    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args, **kwargs)
