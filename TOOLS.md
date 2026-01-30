# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## 环境信息

### 运行环境
- **平台:** GitHub Codespaces
- **工作路径:** `/workspaces/clawdbot`
- **公网地址:** https://fictional-space-train-rp5vjxx9rwj2p4xp-18792.app.github.dev/
- **Node.js:** v24.11.1
- **系统:** Ubuntu Linux

### OpenClaw 安装位置
- **Gateway:** `/usr/local/share/nvm/versions/node/v24.11.1/lib/node_modules/openclaw/`
- **Workspace:** `/home/codespace/.openclaw/workspace/`

## 已安装的 CLI 工具

### AI 编程助手
- **claude** (Claude Code v2.1.25) → 配置为使用 Kimi Code API
- **codex** (Codex CLI v0.92.0) → OpenAI Codex
- **gemini** (Google Gemini CLI v0.26.0)

### 其他工具
- **clawdhub** v0.3.0 - 技能管理
- **yt-dlp** v2026.01.29 - 视频下载
- **fkill** - 进程管理
- **tweet** - Twitter/X CLI
- **playwright** v1.58.0 - 浏览器自动化
- **elevenlabs** - 语音合成
- **http-server / serve** - 静态服务器

## 配置信息

### Claude Code + Kimi 配置
```bash
export ANTHROPIC_BASE_URL="https://api.kimi.com/coding/"
export ANTHROPIC_API_KEY="sk-kimi-Ac88NAoi8F5HIHbD90f9oCVUC2sQr4J6MUT9v4P746sajLHsb0VbRAJhuW1a9hwF"
```

### 定时任务
- **北京天气播报** - 每小时推送一次

---

*更新于 2026-01-30*
