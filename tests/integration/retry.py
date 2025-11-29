import asyncio
import logging
import random
from typing import Callable, Iterable, Tuple, Any

logger = logging.getLogger("integration.retry")


async def retry_async(
    coro_func: Callable,
    *args,
    attempts: int = 3,
    exceptions: Iterable[Exception] = (OSError, ConnectionError, asyncio.TimeoutError, TimeoutError),
    initial_delay: float = 1.0,
    max_delay: float = 8.0,
    jitter: bool = True,
    logger_obj: logging.Logger | None = None,
    **kwargs,
) -> Any:
    """Call an async function with retries using exponential backoff and optional jitter.

    Parameters:
    - coro_func: async callable to invoke
    - attempts: total number of attempts (including first)
    - exceptions: iterable of exception classes to catch and retry on
    - initial_delay: delay before first retry
    - max_delay: maximum backoff delay
    - jitter: add uniform random jitter to backoff
    - logger_obj: optional logger to use; falls back to module logger
    - args/kwargs: passed to coro_func

    Raises the last exception if all attempts fail.
    """
    log = logger_obj or logger
    delay = initial_delay
    last_exc = None

    for attempt in range(1, attempts + 1):
        try:
            if attempt > 1:
                log.debug("Retry attempt %d/%d calling %s", attempt, attempts, getattr(coro_func, "__name__", repr(coro_func)))
            return await coro_func(*args, **kwargs)
        except Exception as e:
            # Only retry on configured exception types
            if not isinstance(e, tuple(exceptions)):
                raise

            last_exc = e
            if attempt == attempts:
                log.error(
                    "All %d attempts failed for %s: %s",
                    attempts,
                    getattr(coro_func, "__name__", repr(coro_func)),
                    e,
                )
                break

            # compute next delay with exponential backoff and optional jitter
            sleep_time = delay
            if jitter:
                sleep_time = random.uniform(0, delay)

            log.warning(
                "Attempt %d/%d failed with %s: %s. Retrying in %.2fs",
                attempt,
                attempts,
                type(e).__name__,
                e,
                sleep_time,
            )

            await asyncio.sleep(sleep_time)
            delay = min(delay * 2, max_delay)

    # re-raise the last caught exception
    raise last_exc
