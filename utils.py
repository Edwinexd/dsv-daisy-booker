"""
A discord bot capable of booking student group rooms and staff rooms via Daisy (administration tool for Department of Computer and Systems Sciences at Stockholm University)
Copyright (C) 2024 Edwin Sundberg

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import asyncio
import functools
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
    partial_func = functools.partial(func, **kwargs)
    return await loop.run_in_executor(None, partial_func, *args)
