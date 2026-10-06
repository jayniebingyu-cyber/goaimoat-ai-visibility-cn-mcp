"""GoAI Moat — AI 可见性 MCP（中文版 · 纯转发薄壳）

薄壳：本 MCP 不持任何 API 密钥、不计费、不调 subprocess。
所有密钥、账户管理、配额与真实多模型测评都在 GoAI Moat 香港服务器上。
本服务只把调用者身份（api_key / license_key / email）转发到服务器 /api/audit 并回传结果。
"""
from fastmcp import FastMCP
import os, json, urllib.request, urllib.error

AUDIT_URL = os.environ.get("AUDIT_URL", "http://127.0.0.1:8031")

mcp = FastMCP(
    name="GoAI Moat — AI 可见性",
    instructions=(
        "任意网站或品牌的 AI 可见性审计（中文版）。本服务是纯转发薄壳：密钥与配额判断都在服务器端。"
        "用 audit_ai_visibility(url, api_key) 做完整审计；check_ai_mentions(brand) 快速查询；"
        "check_license(license_key) 激活 license 获取 api_key。"
    ),
)


def _post(path, payload):
    req = urllib.request.Request(
        AUDIT_URL.rstrip("/") + path,
        data=json.dumps(payload).encode(),
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=900) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode())
        except Exception:
            return {"ok": False, "error": f"HTTP {e.code}"}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"[:120]}


@mcp.tool()
def audit_ai_visibility(url: str, api_key: str = "", license_key: str = "", email: str = "") -> dict:
    """网站完整 AI 可见性审计（多模型 AI 提及 + GEO/SEO + 0-100 评分）。

    薄壳转发：你的 api_key（或 license_key/email）会被转发到 GoAI Moat 服务器，
    由服务器完成鉴权、配额判断与真实测评。所有密钥都在服务器端。

    Args:
        url: 网站地址（如 "https://example.com"）。
        api_key: 你的 GoAI Moat api_key（购买后用 check_license 激活获取）。
        license_key: Gumroad license 密钥（api_key 的替代）。
        email: 你的邮箱（用于免费 3 次试用）。
    """
    return _post("/api/audit", {
        "url": url, "tier": "audit",
        "api_key": api_key, "license_key": license_key, "email": email,
    })


@mcp.tool()
def check_ai_mentions(brand: str, api_key: str = "", email: str = "") -> dict:
    """快速查询：ChatGPT、Perplexity、Grok 对某品牌的真实说法。

    Args:
        brand: 品牌名（如 "RolePaths"）。
        api_key: 你的 GoAI Moat api_key（可选；email 免费试用亦可）。
        email: 你的邮箱（用于免费试用）。
    """
    return _post("/api/audit", {"brand": brand, "api_key": api_key, "email": email})


@mcp.tool()
def check_license(license_key: str, email: str = "") -> dict:
    """激活 Gumroad license，换取 GoAI Moat api_key。

    Args:
        license_key: 购买后获得的 Gumroad license 密钥。
        email: 绑定 api_key 的邮箱。
    """
    return _post("/api/activate", {"license_key": license_key, "email": email})


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        mcp.run(transport="streamable-http", host=os.getenv("MCP_HOST", "127.0.0.1"),
                port=int(os.getenv("MCP_PORT", "8021")))
    else:
        mcp.run()
