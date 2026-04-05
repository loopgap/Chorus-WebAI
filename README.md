# Chorus-WebAI | 网页 AI 协同引擎

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/driven_by-Playwright-green.svg)](https://playwright.dev/)
[![Status](https://img.shields.io/badge/status-Orchestrator_v2-purple.svg)]()

**Chorus-WebAI** 是一款工业级的 **“元编排器 (Meta-Orchestrator)”**。它通过独创的自动化协同机制，将 DeepSeek、Kimi、通义千问等主流网页 AI 平台无缝集成，构建起一个高效、低成本的分布式 AI 任务执行网络。

## 🎖️ 核心技术特色

Chorus-WebAI 致力于提供最稳定、透明且易于扩展的 Web 自动化体验：

### 1. 🎼 多模型接力 (Multi-Model Relay)
支持任务间的深度上下文流转。您可以在编排复杂的业务流：
- **逻辑生成**: 利用 A 模型生成需求大纲。
- **内容扩写**: 自动引用前序结果（通过 `{prev_result}` 占位符）让 B 模型进行精细化填充。
- **合规审计**: 由 C 模型完成最终的质量与合规性交叉检查。

### 2. ⚓ 语义锚点定位 (Semantic Anchor)
采用自愈式元素识别技术。引擎结合了 **A11y 辅助功能树** 与 **模糊视觉特征**，即使网页 UI 发生结构性变动或类名混淆，指挥官也能凭借“操作意图”精准锁定目标。

### 3. 🔍 视觉证据链 (Visual Evidence Chain)
执行过程全透明。系统自动记录全链路网络请求、DOM 变更以及关键节点的 **“黑匣子截图”**。在任务异常时，为您提供可交互的现场复现报告。

### 4. 💰 极致经济性 (Zero-API Strategy)
充分利用网页端 AI 的原生性能。无需配置昂贵的 API Key，通过模拟人类直觉的交互节奏，在保障账号安全的前提下实现大规模生产力自动化。

## ✅ 交付标准与质量保障

为了确保工业级可靠性，项目内置了全套质量门禁：
- **自动化测试**：44 项覆盖核心操作链路的单元测试。
- **性能监控**：模块导入 < 2s，UI 构建 < 12s，TB 级历史记录反向读取 O(1) 内存占用。
- **质量门禁**：集成 Ruff 静态检查与质量自动校验脚本。

