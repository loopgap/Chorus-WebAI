# ShadowBoard API Documentation

**Note**: ShadowBoard (test_mcp) is a **Gradio web UI application** with browser automation, not a REST API. It does not expose HTTP endpoints for external consumption.

This document describes:
1. Internal Python module API (for developers)
2. Gradio UI "events" (user-facing interface)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   Web UI (Gradio)                   │
│                  web_app.py                         │
└─────────────────────┬───────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   ┌─────────┐  ┌──────────┐  ┌──────────┐
   │  Core   │  │ Services │  │   UI     │
   │ src/core│  │src/services│ │ src/ui  │
   └─────────┘  └──────────┘  └──────────┘
```

---

## Internal Python API

### Configuration (`src/core/config.py`)

```python
get_config_manager() -> ConfigManager
```

**Configuration Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `target_url` | string | Target AI chat URL |
| `browser_channel` | string | Playwright browser channel |
| `send_mode` | string | "enter" or "button" |
| `max_retries` | int | Max retry attempts |
| `response_timeout_seconds` | int | Response timeout |

### Dependencies (`src/core/dependencies.py`)

```python
get_task_tracker() -> TaskTracker
get_memory_store() -> MemoryStore
get_session_manager() -> SessionManager
get_workflow_engine() -> WorkflowEngine
get_monitor() -> MetricsCollector
```

### Task Tracker (`src/services/task_tracker.py`)

```python
TaskTracker.create_task(task_id: str, config: dict) -> Task
TaskTracker.start_task(task_id: str) -> None
TaskTracker.complete_task(task_id: str, response: str) -> None
TaskTracker.fail_task(task_id: str, error: str) -> None
TaskTracker.list_tasks(status: str = None, limit: int = 100) -> List[Task]
```

### Memory Store (`src/services/memory_store.py`)

```python
MemoryStore.create_session(session_id: str, metadata: dict = None) -> Session
MemoryStore.add_message(session_id: str, role: str, content: str, **metadata) -> Message
MemoryStore.get_context(session_id: str, max_messages: int = 20) -> List[Message]
MemoryStore.list_sessions(limit: int = 50) -> List[Session]
MemoryStore.search_messages(query: str, session_id: str = None, limit: int = 20) -> List[Message]
```

### Workflow Engine (`src/services/workflow.py`)

```python
WorkflowEngine.register_workflow(workflow: Workflow) -> None
WorkflowEngine.list_workflows() -> List[Workflow]
WorkflowEngine.execute(workflow_id: str, context: dict = None) -> dict
```

### Monitor/Metrics (`src/services/monitor.py`)

```python
MetricsCollector.increment(name: str, value: float = 1.0, tags: dict = None) -> None
MetricsCollector.gauge(name: str, value: float, tags: dict = None) -> None
MetricsCollector.observe(name: str, value: float, tags: dict = None) -> None
MetricsCollector.get_metrics_since(since: datetime, name_prefix: str = None) -> List[Metric]
```

---

## Gradio UI Events

The web UI exposes the following interactive "events" (buttons and inputs):

### Setup Tab Events

| Event | Handler | Description |
|-------|---------|-------------|
| `应用平台预设` | `_apply_provider` | Apply provider preset (DeepSeek/Kimi/etc) |
| `保存参数` | `_save_config_from_form` | Save configuration to disk |
| `打开登录浏览器` | `_open_login_browser` | Open browser for login |
| `登录完成检查` | `_finish_login_check` | Verify login success |
| `执行冒烟测试` | `_run_smoke_test` | Run smoke test with confirmation |
| `一键准备` | `_one_click_prepare` | One-click login preparation |

### Task Tab Events

| Event | Handler | Description |
|-------|---------|-------------|
| `开始执行` | `_run_task` | Execute task with selected template |
| `复用上次输入` | `_reuse_last_input` | Load last used template/input |
| `导出结果` | `_export_response` | Export response to file |
| Template Change | `_template_help` | Show template usage guide |
| Input Change | `_input_tip` | Show input length tips |

### History Tab Events

| Event | Handler | Description |
|-------|---------|-------------|
| `刷新历史` | `_history_table` | Refresh history table |
| `清空历史` | `_clear_history` | Clear all history |
| `健康检查` | `_health_check` | Show system health status |
| `查看最近错误日志` | `_latest_errors` | Show recent error logs |

### Queue Tab Events

| Event | Handler | Description |
|-------|---------|-------------|
| `加入队列` | `add_to_queue` | Add task to batch queue |
| `刷新队列` | `render_queue_table` | Refresh queue display |
| `清空队列` | `clear_queue` | Clear entire queue |
| `执行队列首个任务` | `process_queue_once` | Execute first queued task |

---

## Entry Points

| File | Purpose |
|------|---------|
| `main.py` | CLI entry point for core automation |
| `web_app.py` | Web UI launcher (Gradio) |
| `perf_check.py` | Performance checking script |

---

## Data Models

### Task (`src/models/task.py`)
```python
class Task:
    task_id: str
    status: TaskStatus  # pending, running, completed, failed
    priority: TaskPriority  # low, normal, high
    created_at: datetime
    completed_at: Optional[datetime]
```

### Session (`src/models/session.py`)
```python
class Session:
    session_id: str
    state: SessionState
    created_at: datetime
    last_activity: datetime

class Message:
    message_id: str
    session_id: str
    role: str  # user, assistant
    content: str
    created_at: datetime
```

---

## Supported Platforms

| Platform | URL | Send Mode |
|----------|-----|-----------|
| DeepSeek | https://chat.deepseek.com/ | enter |
| Kimi | https://kimi.moonshot.cn/ | enter/button |

---

## Internal API Documentation

For detailed module-level API reference (configuration, services, UI components), see [API-Reference.md](./API-Reference.md).

---

## Browser Automation Interface

ShadowBoard uses Playwright for browser automation. Key functions in `main.py`:

```python
open_chat_page(config: dict) -> Tuple[Playwright, BrowserContext, Page]
send_with_retry(config: dict, prompt: str) -> AsyncGenerator[str, None]
get_first_visible_locator(page: Page, selectors: dict, timeout_ms: int) -> Optional[Locator]
```