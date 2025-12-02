# utils.py
import logging
import traceback
import functools
import inspect
from typing import Any

from github import GithubException, RateLimitExceededException

# -----------------------------
# Logger configuration
# -----------------------------
logger = logging.getLogger("github_tools")
logger.setLevel(logging.DEBUG)  # Adjust as needed
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


# -----------------------------
# LLM-safe error envelope
# -----------------------------
def error_response(message: str, *, details: dict | None = None) -> dict:
    """
    Construct a standard, LLM-safe error dictionary.
    """
    payload = {"error": {"message": message}}
    if details:
        payload["error"]["details"] = details
    return payload


# -----------------------------
# Exception utilities
# -----------------------------
def _is_error_envelope(value: Any) -> bool:
    """Check if value looks like an LLM-safe error envelope."""
    return isinstance(value, dict) and "error" in value


def _format_exc_details(exc: BaseException) -> dict:
    """Return minimal structured exception details for LLM-safe output."""
    tb = traceback.format_exc()
    return {
        "type": type(exc).__name__,
        "message": str(exc),
        "traceback_snippet": tb.splitlines()[-10:] if tb else [],
    }


# -----------------------------
# Decorator: tool_safety
# -----------------------------
def tool_safety(tool_name: str, *, include_traceback: bool = False):
    """
    Decorator to wrap agent tools and convert exceptions into LLM-safe error envelopes.
    """
    def decorator(func):
        is_coro = inspect.iscoroutinefunction(func)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                if _is_error_envelope(result):
                    return result
                return result
            except Exception as e:
                logger.exception("[%s] Unexpected exception: %s", tool_name, e)
                details = _format_exc_details(e)
                if not include_traceback:
                    details.pop("traceback_snippet", None)
                return error_response(f"{tool_name}: unexpected error", details=details)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if inspect.isawaitable(result):
                    logger.error("[%s] Sync wrapper got awaitable", tool_name)
                    return error_response(f"{tool_name}: internal misconfiguration")
                if _is_error_envelope(result):
                    return result
                return result
            except Exception as e:
                logger.exception("[%s] Unexpected exception: %s", tool_name, e)
                details = _format_exc_details(e)
                if not include_traceback:
                    details.pop("traceback_snippet", None)
                return error_response(f"{tool_name}: unexpected error", details=details)

        return async_wrapper if is_coro else sync_wrapper

    return decorator
