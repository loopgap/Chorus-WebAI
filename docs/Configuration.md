# 配置手册 (Configuration)

本手册详细介绍了 ShadowBoard 的配置体系。

---

## ⚙️ 配置全集 (Configuration Schema)

配置文件位于 `.semi_agent/config.json`，支持实时修改：

| 配置项 | 类型 | 默认值 | 说明 | 进阶建议 |
| :--- | :--- | :--- | :--- | :--- |
| `target_url` | String | `https://chat.deepseek.com/` | 自动化进入的初始页面 | 可在"平台预设"中一键切换 |
| `browser_channel` | String | `msedge` | 浏览器内核 | 推荐使用 `msedge` 或 `chrome` |
| `send_mode` | Enum | `enter` | 发送触发方式 | `enter` (回车) / `button` (点击按钮) |
| `max_retries` | Integer | `3` | 任务失败后的重试次数 | 建议设为 3，配合线性回退算法 |
| `response_timeout_seconds` | Integer | `120` | 等待 AI 响应的最长时间 | 长文本生成建议设为 300 以上 |
| `stable_response_seconds` | Integer | `3` | 判断生成结束的静默时长 | 内容变动停止 N 秒后认为生成完成 |
| `confirm_before_send` | Boolean | `true` | 发送前是否弹出二次确认 | 批量队列执行时会自动强制关闭 |

### 环境变量支持

配置项可通过环境变量覆盖，格式为 `SHADOW_<UPPERCASE_KEY>`：

```powershell
# Windows 示例
$env:SHADOW_MAX_RETRIES=5
$env:SHADOW_TARGET_URL="https://kimi.moonshot.cn/"

# Linux/macOS 示例
export SHADOW_MAX_RETRIES=5
export SHADOW_TARGET_URL="https://kimi.moonshot.cn/"
```

---

## 2. Provider 配置

内置支持多个 AI 平台，通过 `ConfigManager.get_provider()` 获取：

| Provider | URL | 发送方式 | 说明 |
| :--- | :--- | :--- | :--- |
| deepseek | https://chat.deepseek.com/ | 回车 | 建议开启'回车发送' |
| kimi | https://kimi.moonshot.cn/ | 回车 | 长文本分析效果好 |
| tongyi | https://tongyi.aliyun.com/ | 点击按钮 | 通义建议使用'点击按钮'模式 |

---

## 3. 状态目录结构

`ConfigManager` 自动管理以下目录（`.semi_agent/` 下）：

| 目录 | 说明 |
| :--- | :--- |
| `config.json` | 运行配置 |
| `browser_profile/` | 浏览器登录状态 |
| `errors/` | 错误日志 |
| `history.jsonl` | 历史记录 |
| `exports/` | 导出文件 |
| `docs/` | 接口文档 |

---

[返回文档中心](Home.md)
