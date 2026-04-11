# 开发与维护 (Development)

本文档面向希望扩展或自定义 ShadowBoard 的开发者。

---

## 🛠️ 统一管理工具 (`sb.go`)

我们使用 Go 编写了一个跨平台的任务运行器，用于简化日常操作：

```powershell
# 环境初始化
go run sb.go setup

# 运行 Web UI (Boardroom)
go run sb.go web

# 执行全量质量校验 (Quality Gate)
go run sb.go check

# 仅运行单元测试
go run sb.go test
```

## 📁 项目结构 (Structure)

*   `src/core/`：Playwright 自动化引擎、浏览器管理、配置解析。
*   `src/services/`：三大核心业务服务（任务、记忆、监控）。
*   `src/models/`：数据模型定义。
*   `tests/`：完整的单元测试与集成测试集。

---

[返回首页](Home.md)
