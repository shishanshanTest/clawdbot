# AI News Radar - 实时资讯雷达

一个自动抓取 AI 行业资讯、计算热度并推送到飞书的 Python 项目。

## 📋 功能特性

- 🤖 **多源数据抓取**：支持 OpenAI Blog、Anthropic Blog、Hacker News、GitHub Trending
- 🔥 **热度计算**：基于来源权重和发布时间的智能排序
- 🚀 **飞书推送**：自动推送 Top 5 热点资讯到飞书群
- ⏰ **定时调度**：每小时自动运行一次
- 🛡️ **异常处理**：单个数据源失败不影响整体流程

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置飞书 Webhook

飞书 Webhook URL 已配置在 `config.py` 中：
```python
FEISHU_WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/3df64af8-27cc-4e52-bc19-03d2deb176ef"
```

### 3. 运行一次测试

```bash
python main.py
```

### 4. 启动定时调度

```bash
python scheduler.py
```

## 📁 项目结构

```
ai-news-radar/
├── fetchers/           # 数据抓取模块
│   ├── __init__.py
│   ├── openai_fetcher.py      # OpenAI Blog RSS
│   ├── anthropic_fetcher.py   # Anthropic Blog RSS
│   ├── hackernews_fetcher.py  # Hacker News API
│   └── github_fetcher.py      # GitHub Trending
├── data/               # 数据存储目录
│   └── processed.json  # 已处理的文章记录
├── config.py           # 配置文件
├── processor.py        # 数据处理（统一格式、去重、热度计算）
├── pusher.py          # 飞书 Webhook 推送
├── scheduler.py       # 定时任务调度
├── main.py            # 主入口
├── requirements.txt   # Python 依赖
└── README.md          # 项目文档
```

## 🔧 配置说明

### 来源权重配置

在 `config.py` 中修改来源权重：

```python
SOURCE_WEIGHTS = {
    "OpenAI Blog": 50,
    "Anthropic Blog": 50,
    "GitHub Trending": 40,
    "Hacker News": 30,
}
```

### 关键词过滤

在 `config.py` 中修改 Hacker News 的关键词：

```python
AI_KEYWORDS = ["AI", "LLM", "GPT", "Claude", "Model", "Machine Learning"]
```

## 📊 热度计算规则

```
hot_score = source_weight + recency_bonus

时间加成：
- 发布时间 ≤ 1 小时：+20
- 发布时间 ≤ 3 小时：+10
- 发布时间 > 3 小时：+0
```

## 🕐 定时任务

项目使用 APScheduler 实现每小时运行一次：

```python
# scheduler.py 中配置
scheduler.add_job(
    run_news_radar,
    'interval',
    hours=1,
    id='news_radar_job',
    replace_existing=True
)
```

## 📝 日志

日志保存在控制台输出，包含：
- 数据抓取状态
- 处理的文章数量
- 推送结果

## 🔌 扩展新数据源

1. 在 `fetchers/` 目录下创建新的 fetcher 文件
2. 实现 `fetch()` 方法，返回统一格式的数据列表
3. 在 `main.py` 中导入并调用新的 fetcher

统一数据格式：
```json
{
  "id": "唯一ID",
  "title": "资讯标题",
  "summary": "简要摘要",
  "link": "原文链接",
  "source": "来源名称",
  "published_at": "ISO8601时间",
  "collected_at": "ISO8601时间",
  "hot_score": 0
}
```

## 🐛 测试模式

运行 `main.py` 时会自动检测测试模式：
- 在 Codespaces 环境中，推送前会询问确认
- 可以通过修改 `TEST_MODE` 配置控制是否实际推送

## 📄 License

MIT License
