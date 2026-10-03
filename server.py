"""GoAI Moat — AI 可见性 MCP（中文版）

多模型 AI 可见性审计：同时问 ChatGPT（消费者版）、Perplexity、Grok 对品牌的真实认知，
扫描网站 GEO/SEO 健康度，返回 0–100 评分 + 基准分位 + 优先问题清单。

定价：免费 3 次/邮箱；之后 $98/月订阅（每天 10 次、每月 100 次）。
"""
from fastmcp import FastMCP
import os, json, sys, time
from pathlib import Path

# 复用核心审计逻辑（同目录 geo_seo_audit.py）
sys.path.insert(0, str(Path(__file__).parent))
from geo_seo_audit import scan_site, infer_brand, ai_probe, score_site

QUOTA_DIR = os.environ.get("QUOTA_DIR", "/opt/gg-ai-brief/ai-visibility-cn")
FREE_LIMIT = 3          # 免费 3 次/邮箱
DAILY_LIMIT = 10        # 订阅后每天 10 次
MONTHLY_LIMIT = 100     # 订阅后每月 100 次
LICENSE_PRICE = "$98/月（每天 10 次、每月 100 次）"
BUY_LINK = "https://niebingyu.gumroad.com/l/ai-visibility"

mcp = FastMCP(
    name="GoAI Moat — AI 可见性",
    instructions=(
        "任意网站或品牌的 AI 可见性审计（中文版）。同时问 ChatGPT、Perplexity、Grok 对品牌的真实认知，"
        "扫描网站 GEO/SEO 健康度，返回 0–100 评分 + 基准分位 + 优先问题清单。"
        "免费 3 次/邮箱；之后 $98/月订阅（每天 10 次、每月 100 次）。"
    ),
)


def _quota_file():
    return Path(QUOTA_DIR) / "quota.json"


def _load_quota():
    f = _quota_file()
    if f.exists():
        try:
            return json.loads(f.read_text())
        except Exception:
            pass
    return {}


def _save_quota(q):
    _quota_file().parent.mkdir(parents=True, exist_ok=True)
    _quota_file().write_text(json.dumps(q, ensure_ascii=False, indent=2))


def _now():
    return int(time.time())


def _check_access(email: str) -> dict:
    """检查额度。返回 {"ok": bool, "reason": str}"""
    if not email:
        return {"ok": False, "reason": "请提供 email 参数（用于记录免费额度）"}
    q = _load_quota()
    rec = q.get(email, {})
    now = _now()

    if rec.get("license_until", 0) > now:
        today = time.strftime("%Y-%m-%d")
        month = time.strftime("%Y-%m")
        if rec.get("daily_date") != today:
            rec["daily_date"] = today
            rec["daily_count"] = 0
        if rec.get("daily_count", 0) >= DAILY_LIMIT:
            q[email] = rec
            _save_quota(q)
            return {"ok": False, "reason": f"已达每日上限（{DAILY_LIMIT} 次/天）"}
        if rec.get("monthly_month") != month:
            rec["monthly_month"] = month
            rec["monthly_count"] = 0
        if rec.get("monthly_count", 0) >= MONTHLY_LIMIT:
            q[email] = rec
            _save_quota(q)
            return {"ok": False, "reason": f"已达每月上限（{MONTHLY_LIMIT} 次/月）"}
        rec["daily_count"] = rec.get("daily_count", 0) + 1
        rec["monthly_count"] = rec.get("monthly_count", 0) + 1
        q[email] = rec
        _save_quota(q)
        return {"ok": True, "reason": f"订阅中（今日 {rec['daily_count']}/{DAILY_LIMIT}）"}

    if rec.get("count", 0) < FREE_LIMIT:
        rec["count"] = rec.get("count", 0) + 1
        q[email] = rec
        _save_quota(q)
        return {"ok": True, "reason": f"免费 {rec['count']}/{FREE_LIMIT}"}

    return {"ok": False, "reason": f"免费额度已用尽（{FREE_LIMIT} 次）。订阅 {LICENSE_PRICE}：{BUY_LINK}"}


@mcp.tool()
def check_license(license_key: str, email: str) -> dict:
    """激活月度订阅 license（$98/月，每天 10 次、每月 100 次）。

    Args:
        license_key: license 密钥（以 "av-" 开头）。
        email: 绑定 license 的邮箱。
    """
    if not license_key.startswith("av-"):
        return {"ok": False, "message": "license 密钥无效"}
    q = _load_quota()
    rec = q.get(email, {})
    rec["license_until"] = _now() + 30 * 86400
    rec["daily_date"] = ""
    rec["monthly_month"] = ""
    q[email] = rec
    _save_quota(q)
    return {"ok": True, "message": f"订阅已激活 30 天（{DAILY_LIMIT} 次/天，{MONTHLY_LIMIT} 次/月）"}


@mcp.tool()
def audit_ai_visibility(url: str, email: str = "") -> dict:
    """网站的完整 AI 可见性审计：多模型 AI 提及 + GEO/SEO 健康度 + 0–100 评分 + 基准分位。

    同时问 ChatGPT（消费者版）、Perplexity、Grok 对品牌的真实认知，扫描网站技术健康度，
    返回综合评分、基准分位和按优先级排序的问题清单。

    Args:
        url: 网站地址（如 "https://example.com"）。
        email: 你的邮箱（用于记录额度）。
    """
    access = _check_access(email)
    if not access["ok"]:
        return {"ok": False, "quota": access["reason"]}

    url = url.strip().rstrip("/")
    if not url.startswith("http"):
        url = "https://" + url

    checks = scan_site(url)
    if not checks.get("accessible"):
        return {"ok": False, "url": url, "error": "网站无法访问", "detail": checks.get("error")}

    brand = infer_brand(checks)
    probe = ai_probe(brand)
    s = score_site(checks, probe)

    return {
        "ok": True,
        "url": url,
        "品牌": brand,
        "综合评分": s["total"],
        "seo评分": s["seo"],
        "geo评分": s["geo"],
        "基准分位": s["percentile"],
        "AI提及": [
            {"模型": p["model"], "角度": p["angle"], "是否提及": p["mentioned"], "回答": p["answer"]}
            for p in probe
        ],
        "quota": access["reason"],
    }


@mcp.tool()
def check_ai_mentions(brand: str, email: str = "") -> dict:
    """快速查询：ChatGPT、Perplexity、Grok 对一个品牌的真实说法。

    返回各模型的提及情况和回答，不包含完整网站扫描。

    Args:
        brand: 品牌名（如 "RolePaths"）。
        email: 你的邮箱（用于记录额度）。
    """
    access = _check_access(email)
    if not access["ok"]:
        return {"ok": False, "quota": access["reason"]}

    probe = ai_probe(brand.strip())
    mentioned = [p["model"] for p in probe if p.get("mentioned")]
    return {
        "ok": True,
        "品牌": brand.strip(),
        "被提及的模型": mentioned,
        "快照": [
            {"模型": p["model"], "角度": p["angle"], "是否提及": p["mentioned"], "回答": p["answer"]}
            for p in probe
        ],
        "quota": access["reason"],
    }


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        mcp.run(transport="streamable-http", host=os.getenv("MCP_HOST", "127.0.0.1"),
                port=int(os.getenv("MCP_PORT", "8021")))
    else:
        mcp.run()
