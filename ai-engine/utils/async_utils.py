"""异步工具模块。

统一封装“把同步阻塞逻辑放到线程中执行”的入口，避免各服务层
散落着 ``asyncio.to_thread`` 调用。这样后续如果要补超时、限流或并发
控制，只需要在这一层统一收口。
"""

from __future__ import annotations

import asyncio
from functools import partial
from typing import Any, Awaitable, Callable, Iterable


class AsyncExecutionHelper:
    """轻量异步执行工具类。"""

    @staticmethod
    async def run_blocking(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """在线程中执行同步阻塞函数。

        这里统一使用 asyncio.to_thread，将数据库、同步检索等阻塞调用
        从事件循环中挪出去，避免 async 路由里直接跑同步 I/O。
        """
        return await asyncio.to_thread(partial(func, *args, **kwargs))

    @staticmethod
    async def run_blocking_with_timeout(
        timeout: float,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """在线程中执行同步任务，并统一加超时控制。"""
        return await asyncio.wait_for(
            AsyncExecutionHelper.run_blocking(func, *args, **kwargs),
            timeout=timeout,
        )

    @staticmethod
    async def gather_limited(
        tasks: Iterable[Callable[[], Awaitable[Any]]],
        limit: int,
    ) -> list[Any]:
        """限制并发度地执行一组异步任务工厂。

        这里接收“可调用对象列表”，而不是已创建的 coroutine，
        这样可以在进入信号量后再真正创建任务，避免一次性铺开过多工作。
        """
        semaphore = asyncio.Semaphore(limit)

        async def _runner(task_factory: Callable[[], Awaitable[Any]]) -> Any:
            async with semaphore:
                return await task_factory()

        return await asyncio.gather(*(_runner(task_factory) for task_factory in tasks))
