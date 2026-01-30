# AI News Radar Configuration
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# 飞书 Webhook 配置
FEISHU_WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/3df64af8-27cc-4e52-bc19-03d2deb176ef"

# 数据源 RSS/API URL
DATA_SOURCES = {
    "openai": "https://openai.com/blog/rss.xml",
    "anthropic": "https://www.anthropic.com/blog/rss.xml",
    "hackernews": "https://hacker-news.firebaseio.com/v0",
    "github": "https://github.com/trending",
}

# 来源权重配置
SOURCE_WEIGHTS = {
    "OpenAI Blog": 50,
    "Anthropic Blog": 50,
    "GitHub Trending": 40,
    "Hacker News": 30,
}

# AI 关键词（用于 Hacker News 过滤）
AI_KEYWORDS = [
    "AI", "LLM", "GPT", "Claude", "Model", 
    "Machine Learning", "OpenAI", "Anthropic",
    "Neural", "Transformer", "LLaMA", "Gemini"
]

# 热度计算配置
RECENCY_BONUS = {
    1: 20,   # ≤ 1 小时
    3: 10,   # ≤ 3 小时
}

# 推送配置
TOP_N = 5  # 推送前 N 条
PUSH_INTERVAL_HOURS = 1  # 推送间隔（小时）

# 数据存储
PROCESSED_DATA_FILE = DATA_DIR / "processed.json"

# 测试模式（True 时不实际推送）
TEST_MODE = os.environ.get("TEST_MODE", "false").lower() == "true"

# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
