"""
Helper Utilities

Common utility functions used across the application.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

# Template definitions
TEMPLATES: Dict[str, str] = {
    "market_analyst": "你现在是 ShadowBoard 的首席营销官 (CMO)。请从市场规模、竞争对手、用户痛点和增长潜力的角度，深度分析以下议案，并指出 3 个核心市场风险：\n\n{user_input}",
    "tech_lead": "你现在是 ShadowBoard 的首席技术官 (CTO)。请评估以下议案的技术可行性、架构复杂度、潜在技术债以及所需的核心技术栈。如果涉及已有分析，请结合参考：\n\n{user_input}",
    "finance_expert": "你现在是 ShadowBoard 的首席财务官 (CFO)。请对以下议案进行冷酷的成本收益分析，指出潜在的财务黑洞、盈利模式的漏洞以及资金链风险：\n\n{user_input}",
    "risk_manager": "你现在是 ShadowBoard 的风险合规官。请针对以下议案及之前的专家意见，寻找法律、合规、隐私以及逻辑上的致命缺陷，进行'红队测试'：\n\n{user_input}",
    "chairman_summary": "你现在是 ShadowBoard 的董事长。请阅读以下所有董事会成员的辩论记录，总结共识点与核心分歧，并最终给出一个明确的'执行/否决/推迟'建议，附带 3 条行动指令：\n\n{user_input}",
    "summary": "Summarize the following content in 5 bullets:\n\n{user_input}",
    "translation": "Translate the following text to Chinese and keep meaning precise:\n\n{user_input}",
    "rewrite": "Rewrite the following text to be clear and professional:\n\n{user_input}",
    "extract": "Extract key entities, dates, and action items from the following:\n\n{user_input}",
    "qa": "Answer the request below with concise steps:\n\n{user_input}",
}


def build_prompt(template_key: str, user_input: str) -> str:
    """
    Build a prompt from a template.

    Args:
        template_key: Template identifier or "custom"
        user_input: User's input text

    Returns:
        Formatted prompt string
    """
    if template_key == "custom":
        return user_input

    template = TEMPLATES.get(template_key, "{user_input}")
    return template.format(user_input=user_input)


def shorten_text(
    text: str,
    max_length: int = 100,
    placeholder: str = "...",
) -> str:
    """
    Shorten text to maximum length.

    Args:
        text: Input text
        max_length: Maximum length including placeholder
        placeholder: Suffix for truncated text

    Returns:
        Shortened text
    """
    if len(text) <= max_length:
        return text

    # Account for placeholder length
    truncate_at = max_length - len(placeholder)
    if truncate_at <= 0:
        return placeholder[:max_length]

    return text[:truncate_at] + placeholder


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable form.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "2m 30s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"

    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60

    if minutes < 60:
        return f"{minutes}m {remaining_seconds:.0f}s"

    hours = minutes // 60
    remaining_minutes = minutes % 60
    return f"{hours}h {remaining_minutes}m"


def get_timestamp(format: str = "iso") -> str:
    """
    Get current timestamp in specified format.

    Args:
        format: Output format ("iso", "file", "display")

    Returns:
        Formatted timestamp string
    """
    now = datetime.now()

    if format == "iso":
        return now.isoformat(timespec="seconds")
    elif format == "file":
        return now.strftime("%Y%m%d_%H%M%S")
    elif format == "display":
        return now.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return now.isoformat()


def parse_bool(value: Any, default: bool = False) -> bool:
    """
    Parse a value as boolean.

    Args:
        value: Input value (string, bool, int, etc.)
        default: Default if cannot parse

    Returns:
        Boolean value
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lower_value = value.lower()
        if lower_value in ("true", "yes", "1", "on"):
            return True
        if lower_value in ("false", "no", "0", "off"):
            return False
        return default
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def safe_get(
    data: Dict[str, Any],
    *keys: str,
    default: Any = None,
) -> Any:
    """
    Safely get nested dictionary value.

    Args:
        data: Dictionary to search
        *keys: Nested keys
        default: Default value if not found

    Returns:
        Value or default
    """
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current
