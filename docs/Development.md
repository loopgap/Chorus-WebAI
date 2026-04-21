# 开发与维护

本文档描述当前仓库可直接使用的开发流程，内容已与现有文件对齐。

---

## 1. 本地开发启动

```powershell
# 安装依赖（可编辑模式）
pip install -e .

# 安装浏览器内核
playwright install chromium

# 启动 Web UI
python web_app.py
```

## 2. 运行测试

```powershell
# 全量测试
pytest

# 指定测试文件
pytest tests/test_workflow.py

# 性能检查（Gradio 懒加载优化后的启动性能基准）
python perf_check.py
```

> **注意**: `perf_check.py` 测量 `import web_app` 和 `build_ui` 耗时。由于 Gradio 采用懒加载优化（`import gradio` 在 `build_ui()` 函数内部），UI 构建时间包含 Gradio 导入时间。

## 3. 关键目录

- `src/core/`: 配置（config.py）、会话管理（session.py）、异常、浏览器管理、服务依赖。
- `src/core/auth/`: 认证相关模块。
- `src/core/browser/`: 浏览器子模块。
- `src/core/resilience/`: 弹性机制（重试、熔断等）。
- `src/core/security/`: 安全相关模块。
- `src/services/`: 工作流、任务追踪、记忆存储、监控、队列。
- `src/models/`: Task、Session、History 等模型。
- `src/ui/`: Gradio 页面组装与 Tab 业务逻辑。
- `src/ui/components/`: UI 组件（CSS、选择器、HTML 片段）。
- `src/ui/handlers/`: UI 事件处理器。
- `tests/`: 单元测试与集成测试。

## 4. 异步开发规范 (Async First)

由于核心存储迁移至 `aiosqlite`，开发新功能时请遵循：
- **异步存储**: 所有对 `MemoryStore`、`TaskTracker` 或 `Monitor` 的访问必须通过 `await`。
- **服务注入**: 统一从 `src.core.dependencies` 获取单例，并确保在入口处调用过 `initialize_services()`。
- **UI 线程**: 避免在 Gradio 事件处理函数中执行长时间的同步阻塞操作，优先使用 `asyncio`。

## 5. 性能门禁与基准 (Performance Gate)

系统集成严苛的性能检查 `perf_check.py`，防止启动性能退化：
- `import_web_app_seconds`: 必须维持在较低水平。**严禁**在 `web_app.py` 的顶层导入 `gradio` 或 `playwright`，此类导入必须放在 `build_ui` 内部。
- **CI 倍率**: 在 GitHub Actions 中会自动应用 5x 倍率以适配较慢的运行环境。

## 6. 开发约定

- 新增服务优先放在 `src/services/`，模型放在 `src/models/`。
- 业务入口统一通过 `src/core/dependencies.py` 获取服务实例。
- 文档变更后同步更新 [Home.md](Home.md) 的索引。

---

[返回文档中心](Home.md)
