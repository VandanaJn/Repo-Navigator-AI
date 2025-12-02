import pytest
import functools
import inspect
from repo_navigator.sub_agents.tools.utils import (
    tool_safety,
    error_response
)

# --------------------------
# Test error_response
# --------------------------
def test_error_response_basic():
    msg = "Something went wrong"
    result = error_response(msg)
    assert "error" in result
    assert result["error"]["message"] == msg
    assert "details" not in result

def test_error_response_with_details():
    msg = "Failure"
    details = {"foo": "bar"}
    result = error_response(msg, details=details)
    assert result["error"]["details"] == details

# --------------------------
# Test tool_safety decorator
# --------------------------
def test_tool_safety_catches_exception():
    @tool_safety("test_tool")
    def failing_func():
        raise ValueError("Boom!")

    result = failing_func()
    assert "error" in result
    assert "Boom" in result["error"]["details"]["message"]

def test_tool_safety_returns_normal_value():
    @tool_safety("test_tool")
    def success_func():
        return {"value": 42}

    result = success_func()
    assert result["value"] == 42

@pytest.mark.asyncio
async def test_tool_safety_async_function():
    @tool_safety("async_tool")
    async def async_func():
        return {"ok": True}

    result = await async_func()
    assert result["ok"] is True

def test_tool_safety_sync_returns_error_on_awaitable():
    @tool_safety("test_tool")
    def sync_func():
        async def inner():
            return 123
        return inner()
    result = sync_func()
    assert "error" in result
    assert "internal misconfiguration" in result["error"]["message"]
