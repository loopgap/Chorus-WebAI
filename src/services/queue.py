"""Task queue service with asyncio.Lock protection for concurrent access."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Tuple

from src.core.templates import TEMPLATE_LABEL_TO_KEY


@dataclass
class QueueItem:
    """Represents a single item in the task queue."""

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    template_label: str = ""
    user_input: str = ""
    status: str = "等待中"
    result: str = ""
    added_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class TaskQueue:
    """Thread-safe task queue using asyncio.Lock for concurrent access."""

    def __init__(self) -> None:
        self._queue: List[QueueItem] = []
        self._lock: asyncio.Lock | None = None

    def _get_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    @property
    def lock(self) -> asyncio.Lock:
        return self._get_lock()

    @property
    def queue(self) -> List[QueueItem]:
        return self._queue

    def clear(self) -> None:
        """Clear all items from the queue."""
        self._queue.clear()

    def add_item(self, template_label: str, user_input: str) -> QueueItem:
        """Add a new item to the queue. Caller must hold the lock."""
        item = QueueItem(template_label=template_label, user_input=user_input)
        self._queue.append(item)
        return item

    def get_pending(self) -> List[QueueItem]:
        """Get all pending items. Caller must hold the lock."""
        return [item for item in self._queue if item.status == "等待中"]

    def render_table(self) -> List[List[Any]]:
        """Render queue as table data for Gradio Dataframe."""
        return [
            [
                item.id,
                item.added_at,
                item.template_label,
                item.user_input[:20],
                item.status,
                item.result[:30] if item.result else "",
            ]
            for item in self._queue
        ]


# Global singleton instance
_task_queue_instance: TaskQueue | None = None


def get_task_queue() -> TaskQueue:
    """Get the global TaskQueue singleton instance."""
    global _task_queue_instance
    if _task_queue_instance is None:
        _task_queue_instance = TaskQueue()
    return _task_queue_instance


async def add_to_queue(template_label: str, user_input: str) -> str:
    """Add a task to the queue. Returns status message."""
    raw_input = (user_input or "").strip()
    if not raw_input:
        return "提示: 任务内容为空，未加入队列"

    queue = get_task_queue()
    async with queue.lock:
        item = queue.add_item(template_label, raw_input)

    return f"已成功加入队列 (ID: {item.id})，当前队列长度: {len(queue.queue)}"


def render_queue_table() -> List[List[Any]]:
    """Render the current queue state as table data."""
    queue = get_task_queue()
    return queue.render_table()


async def clear_queue() -> Tuple[str, List[List[Any]]]:
    """Clear all items from the queue. Returns status and table."""
    queue = get_task_queue()
    async with queue.lock:
        queue.clear()
    return "队列已清空", render_queue_table()


async def process_queue_once() -> Tuple[str, List[List[Any]]]:
    """Process the first pending task in the queue. Returns status and table."""
    import copy

    from main import build_prompt, load_config, send_with_retry, append_history

    queue = get_task_queue()
    async with queue.lock:
        pending = queue.get_pending()
        if not pending:
            return "队列中没有等待执行的任务", render_queue_table()
        target = pending[0]
        target.status = "执行中"

    cfg = load_config()
    run_cfg = copy.deepcopy(cfg)
    run_cfg["confirm_before_send"] = False
    template_key = TEMPLATE_LABEL_TO_KEY.get(target.template_label, "custom")
    prompt = build_prompt(template_key, target.user_input)

    import time

    started = time.time()
    response = ""
    try:
        async for chunk in send_with_retry(run_cfg, prompt):
            response = chunk
            target.result = f"收到 {len(response)} 字..."
        target.status = "执行成功"
        target.result = response
        ok = True
    except Exception as exc:
        target.status = "执行失败"
        target.result = str(exc)
        ok = False

    elapsed = round(time.time() - started, 2)
    append_history(
        {
            "time": datetime.now().isoformat(timespec="seconds"),
            "template": template_key,
            "input_chars": len(target.user_input),
            "response_chars": len(response),
            "duration_seconds": elapsed,
            "ok": ok,
        }
    )
    return f"任务 {target.id} 已处理完毕 ({target.status})", render_queue_table()
