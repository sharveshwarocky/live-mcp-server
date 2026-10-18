# Live MCP Server

A publicly reachable Model Context Protocol (MCP) server implementing the `solve_challenge` tool.

---

## 🚀 One-Click Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/sharveshwarocky/live-mcp-server)

---

## 📡 Endpoints
- **MCP Endpoint**: `POST /mcp` (Handles JSON-RPC 2.0: `initialize`, `notifications/initialized`, `tools/list`, `tools/call`)
- **Direct Tools List**: `GET /tools/list`
- **Direct Tools Call**: `POST /tools/call` (Reads `X-Exam-Challenge` header)
