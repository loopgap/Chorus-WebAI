from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest

import web_app


@pytest.fixture(autouse=True)
def setup_teardown():
    web_app.TASK_QUEUE.clear()
    yield
    web_app.TASK_QUEUE.clear()


@pytest.mark.asyncio
async def test_add_to_queue_and_process(monkeypatch):
    # Mock task tracker
    mock_tracker = MagicMock()
    mock_tracker.create_task = asyncio.iscoroutinefunction(MagicMock()) # Placeholder
    
    async def fake_create(*args, **kwargs):
        mock = MagicMock()
        mock.id = "t1"
        return mock
        
    monkeypatch.setattr(web_app, "_get_task_tracker", lambda: mock_tracker)
    monkeypatch.setattr(mock_tracker, "create_task", fake_create)
    monkeypatch.setattr(mock_tracker, "start_task", AsyncMock())
    monkeypatch.setattr(mock_tracker, "complete_task", AsyncMock())

    msg = await web_app._add_to_queue("市场分析 (CMO)", "hello")
    assert "t1" in msg
    assert len(web_app.TASK_QUEUE) == 1

    # Mock core.send_with_retry
    async def fake_send(cfg, prompt):
        yield "done"
    monkeypatch.setattr(web_app.core, "send_with_retry", fake_send)
    monkeypatch.setattr(web_app.core, "load_config", lambda: {"confirm_before_send": False})

    status, table = await web_app._process_queue_once()
    assert len(status) > 5
    assert table[0][4] == "执行成功"


@pytest.mark.asyncio
async def test_process_queue_failure(monkeypatch):
    # Mock task tracker
    mock_tracker = MagicMock()
    async def fake_create(*args, **kwargs):
        mock = MagicMock()
        mock.id = "t2"
        return mock
    monkeypatch.setattr(web_app, "_get_task_tracker", lambda: mock_tracker)
    monkeypatch.setattr(mock_tracker, "create_task", fake_create)
    monkeypatch.setattr(mock_tracker, "start_task", AsyncMock())
    monkeypatch.setattr(mock_tracker, "fail_task", AsyncMock())

    await web_app._add_to_queue("市场分析 (CMO)", "fail me")
    
    async def boom(cfg, prompt):
        raise RuntimeError("boom")
        yield ""
    monkeypatch.setattr(web_app.core, "send_with_retry", boom)
    monkeypatch.setattr(web_app.core, "load_config", lambda: {"confirm_before_send": False})

    status, table = await web_app._process_queue_once()
    assert len(status) > 5
    assert table[0][4] == "执行失败"


@pytest.mark.asyncio
async def test_process_empty_queue():
    status, table = await web_app._process_queue_once()
    assert len(status) > 5
    assert len(table) == 0


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)
