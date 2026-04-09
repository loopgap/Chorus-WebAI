"""
性能指标自测工具 (Performance Metrics Checker)

该脚本用于量化关键操作的耗时，包括:
1. 模块导入时间
2. UI 渲染时间
3. 历史数据处理时间
若超过预设阈值，脚本将返回非零退出码，用于 CI/CD 质量门禁。
"""

from __future__ import annotations

import json
import os
import time


def timed(fn, *args, **kwargs):
    t0 = time.perf_counter()
    out = fn(*args, **kwargs)
    dt = time.perf_counter() - t0
    return out, dt


def main() -> int:
    metrics = {}

    t0 = time.perf_counter()
    import web_app  # noqa: F401

    metrics["import_web_app_seconds"] = time.perf_counter() - t0

    import web_app as app

    _, metrics["build_ui_seconds"] = timed(app.build_ui)
    _, metrics["build_guide_seconds"] = timed(app._build_guide_markdown)
    _, metrics["build_api_doc_seconds"] = timed(app._build_api_doc_text)
    _, metrics["history_table_seconds"] = timed(app._history_table, "全部")

    # 基础阈值设置 (针对常规开发机器)
    # import_web_app 包含 gradio 和 playwright，首次加载较慢
    limits = {
        "import_web_app_seconds": 8.0,
        "build_ui_seconds": 15.0,
        "build_guide_seconds": 0.8,
        "build_api_doc_seconds": 0.8,
        "history_table_seconds": 1.0,
    }

    # 环境倍率 (Multiplier): CI 机器性能通常较弱且存在冷启动，允许放宽限制
    is_ci = os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("CI") == "true"
    multiplier = 5.0 if is_ci else 1.0
    
    if is_ci:
        print(f"Detected CI environment. Applying {multiplier}x multiplier to performance thresholds.")

    failed = []
    for k, base_limit in limits.items():
        limit = base_limit * multiplier
        if metrics[k] > limit:
            failed.append({"metric": k, "value": metrics[k], "limit": limit})

    print(json.dumps({"metrics": metrics, "limits": {k: v * multiplier for k, v in limits.items()}, "failed": failed}, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
