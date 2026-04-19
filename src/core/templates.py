from typing import Dict, List

TEMPLATES: Dict[str, str] = {
    "market_analyst": "你现在是 ShadowBoard 的首席营销官 (CMO)。请从市场规模、竞争对手、用户痛点和增长潜力的角度，深度分析以下议案，并指出 3 个核心市场风险：\n\n{user_input}",
    "tech_lead": "你现在是 ShadowBoard 的首席技术官 (CTO)。请评估以下议案的技术可行性、架构复杂度、潜在技术债以及所需的核心技术栈。如果涉及已有分析，请结合参考：\n\n{user_input}",
    "finance_expert": "你现在是 ShadowBoard 的首席财务官 (CFO)。请对以下议案进行冷酷的成本收益分析，指出潜在的财务黑洞、盈利模式的漏洞以及资金链风险：\n\n{user_input}",
    "risk_manager": "你现在是 ShadowBoard 的风险合规官。请针对以下议案及之前的专家意见，寻找法律、合规、隐私以及逻辑上的致命缺陷，进行红队测试：\n\n{user_input}",
    "chairman_summary": "你现在是 ShadowBoard 的董事长。请阅读以下所有董事会成员的辩论记录，总结共识点与核心分歧，并最终给出一个明确的执行/否决/推迟建议，附带 3 条行动指令：\n\n{user_input}",
    "summary": "Summarize the following content in 5 bullets:\n\n{user_input}",
    "translation": "Translate the following text to Chinese and keep meaning precise:\n\n{user_input}",
    "rewrite": "Rewrite the following text to be clear and professional:\n\n{user_input}",
    "extract": "Extract key entities, dates, and action items from the following:\n\n{user_input}",
    "qa": "Answer the request below with concise steps:\n\n{user_input}",
}

PROVIDERS: Dict[str, Dict[str, str]] = {
    "deepseek": {
        "label": "DeepSeek 网页",
        "url": "https://chat.deepseek.com/",
        "send_mode": "enter",
        "guide": "推荐新手首选 页面稳定 先登录后做冒烟测试",
    },
    "kimi": {
        "label": "Kimi 网页",
        "url": "https://kimi.moonshot.cn/",
        "send_mode": "enter",
        "guide": "适合长文处理 登录后先执行一次冒烟验证",
    },
    "tongyi": {
        "label": "通义千问 网页",
        "url": "https://tongyi.aliyun.com/qianwen/",
        "send_mode": "button",
        "guide": "建议使用点击按钮发送 遇到弹窗先手动关闭",
    },
    "doubao": {
        "label": "豆包 网页",
        "url": "https://www.doubao.com/chat/",
        "send_mode": "enter",
        "guide": "登录后建议先做冒烟测试 再开始批量任务",
    },
    "zhipu": {
        "label": "智谱清言 网页",
        "url": "https://chatglm.cn/main/alltoolsdetail",
        "send_mode": "button",
        "guide": "建议点击按钮发送 页面改版时优先检查输入框定位",
    },
    "wenxin": {
        "label": "文心一言 网页",
        "url": "https://yiyan.baidu.com/",
        "send_mode": "button",
        "guide": "登录验证较严格 建议先人工完成验证后再自动执行",
    },
}

PROVIDER_LABEL_TO_KEY: Dict[str, str] = {v["label"]: k for k, v in PROVIDERS.items()}

TEMPLATE_LABEL_TO_KEY: Dict[str, str] = {
    "市场分析 (CMO)": "market_analyst",
    "技术评估 (CTO)": "tech_lead",
    "财务审计 (CFO)": "finance_expert",
    "风险管理 (Red Team)": "risk_manager",
    "董事长总结 (Chairman)": "chairman_summary",
    "摘要总结": "summary",
    "中英翻译": "translation",
    "润色改写": "rewrite",
    "信息抽取": "extract",
    "问答助手": "qa",
    "自定义原样发送": "custom",
}

KEY_TO_TEMPLATE_LABEL: Dict[str, str] = {
    "market_analyst": "市场分析 (CMO)",
    "tech_lead": "技术评估 (CTO)",
    "finance_expert": "财务审计 (CFO)",
    "risk_manager": "风险管理 (Red Team)",
    "chairman_summary": "董事长总结 (Chairman)",
    "summary": "摘要总结",
    "translation": "中英翻译",
    "rewrite": "润色改写",
    "extract": "信息抽取",
    "qa": "问答助手",
    "custom": "自定义原样发送",
    "smoke": "冒烟测试",
}

TEMPLATE_GUIDE: Dict[str, str] = {
    "市场分析 (CMO)": "从市场规模、竞争对手、用户痛点角度分析议案",
    "技术评估 (CTO)": "评估技术可行性、架构复杂度与核心栈",
    "财务审计 (CFO)": "进行成本收益分析，识别财务风险",
    "风险管理 (Red Team)": "从法律合规和逻辑漏洞角度做风险评估",
    "董事长总结 (Chairman)": "汇总分歧与共识并给出最终建议",
    "摘要总结": "适合长文快速提炼要点 默认输出结构化结论",
    "中英翻译": "输入任意语言文本 自动翻译并尽量保留语气",
    "润色改写": "适合邮件 汇报 简历语句优化",
    "信息抽取": "自动提取人名 日期 行动项 截止时间",
    "问答助手": "输入问题后给出简洁可执行步骤",
    "自定义原样发送": "不会套模板 直接把输入内容发送给网页 AI",
}

EXAMPLE_INPUTS: List[List[str]] = [
    [
        "摘要总结",
        "请总结下面会议纪要并输出三条结论和三条行动项\n本周完成接口联调\n下周开始灰度发布\n风险是测试资源不足",
    ],
    ["润色改写", "请把这段话改得专业但简洁 这个功能目前不够稳定 我们后续会持续优化"],
    [
        "信息抽取",
        "从以下文本提取日期 负责人 截止时间 王明二月二十八日前完成验收文档 李华三月一日提交测试报告",
    ],
    ["自定义原样发送", "你是一名项目助理 请把我的需求拆成可执行清单"],
]
