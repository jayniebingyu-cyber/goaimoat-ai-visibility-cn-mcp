# GoAI Moat — AI 可见性 MCP（中文版 · 纯转发薄壳）

多模型 **AI 可见性审计**：同时问 ChatGPT（消费者版）、Perplexity、Grok 对品牌的真实认知，扫描网站 GEO/SEO 健康度，返回 0–100 评分 + 基准分位。

**纯转发薄壳**：本 MCP 不持任何 API 密钥、不计费、不直接调上游。它把你的请求（连同 api_key / license_key / email）转发到 GoAI Moat 香港服务器，由服务器完成鉴权、配额判断与真实测评。MCP 只是发起请求的接口入口。

## 工具

- `audit_ai_visibility(url, api_key=..., license_key=..., email=...)` — 完整审计：多模型 AI 提及 + GEO/SEO + 0–100 评分 + 基准分位 + 优先问题。
- `check_ai_mentions(brand, api_key=..., email=...)` — 快速查询：ChatGPT / Perplexity / Grok 对品牌的真实说法。
- `check_license(license_key, email=...)` — 激活 license 换取 api_key。

## 定价

- **免费**：3 次/邮箱。
- **订阅**：`$98/月`。用 `check_license` 激活。

## 本地运行（stdio）

```bash
pip install -r requirements.txt
python server.py
```

本服务无需任何凭证——鉴权、配额与真实测评都在 GoAI Moat 服务器端。缺少/耗尽 api_key/license/email 时服务器会返回明确错误。

## 托管端点

```
https://ai-visibility-cn.mcp.goaimoat.com/mcp
```

## License

MIT
