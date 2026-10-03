# GoAI Moat — AI 可见性 MCP（中文版）

任意网站或品牌的**多模型 AI 可见性审计**。同时问 ChatGPT（消费者版）、Perplexity、Grok 对品牌的真实认知，扫描网站 GEO/SEO 健康度，返回 0–100 评分 + 基准分位 + 优先问题清单。

## 功能

- `audit_ai_visibility(url)` — 完整审计：多模型 AI 提及 + GEO/SEO 健康度 + 0–100 评分 + 基准分位 + 优先问题。
- `check_ai_mentions(brand)` — 快速查询：ChatGPT / Perplexity / Grok 对品牌的真实说法。

## 为什么值得付费

大多数「AI 可见性」工具只检查**你的网站**。这个 MCP 检查的是 AI 模型**实际怎么说你**——这才是 AI 会不会提及、推荐、忽略你的真相。基准分位（对比 500+ 出海品牌）是你自己调大模型拿不到的数据。

## 定价

- **免费**：每个邮箱 3 次。
- **订阅**：`$98/月` — 每天 10 次、每月 100 次。
- 通过 `check_license(license_key, email)` 激活。

## 本地运行（stdio）

```bash
pip install -r requirements.txt
python server.py
```

启动无需凭证（introspection 可用）。凭证（`MONID_API_KEY`、`SERPER_API_KEY`、`GROK_API_KEY`、`PERPLEXITY_API_KEY`）仅在调用时需要，缺失时工具会返回明确错误。

## 托管端点

```
https://ai-visibility-cn.mcp.goaimoat.com/mcp
```

## License

MIT
