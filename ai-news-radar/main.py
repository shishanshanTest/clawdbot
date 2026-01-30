"""Main Entry - AI News Radar 主入口"""
import logging
import sys
from datetime import datetime
from typing import List, Dict, Any

from config import LOG_LEVEL, LOG_FORMAT
from fetchers import OpenAIFetcher, AnthropicFetcher, HackerNewsFetcher, GitHubFetcher
from processor import DataProcessor
from pusher import FeishuPusher

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


class NewsRadar:
    """AI 资讯雷达主类"""
    
    def __init__(self):
        self.fetchers = [
            OpenAIFetcher(),
            AnthropicFetcher(),
            HackerNewsFetcher(),
            GitHubFetcher(),
        ]
        self.processor = DataProcessor()
        self.pusher = FeishuPusher()
    
    def fetch_all(self) -> List[Dict[str, Any]]:
        """从所有数据源获取文章"""
        logger.info("📡 Fetching articles from all sources...")
        
        all_articles = []
        for fetcher in self.fetchers:
            try:
                articles = fetcher.fetch()
                all_articles.extend(articles)
            except Exception as e:
                logger.error(f"Fetcher {fetcher.__class__.__name__} failed: {e}")
                continue
        
        logger.info(f"📊 Total articles fetched: {len(all_articles)}")
        return all_articles
    
    def run(self, dry_run: bool = False):
        """运行完整流程"""
        # 1. 获取数据
        articles = self.fetch_all()
        
        if not articles:
            logger.info("No articles fetched, skipping push.")
            if not dry_run:
                self.pusher.push([], dry_run=False)
            return
        
        # 2. 处理数据
        top_articles = self.processor.process(articles)
        
        if not top_articles:
            logger.info("No new articles after processing, skipping push.")
            if not dry_run:
                self.pusher.push([], dry_run=False)
            return
        
        # 3. 打印预览
        logger.info("\n" + "=" * 60)
        logger.info("📰 TOP ARTICLES TO PUSH:")
        logger.info("=" * 60)
        for i, article in enumerate(top_articles, 1):
            logger.info(f"\n{i}. [{article['source']}] {article['title']}")
            logger.info(f"   🔥 Score: {article['hot_score']} | 🔗 {article['link']}")
        logger.info("\n" + "=" * 60)
        
        # 4. 推送到飞书
        if dry_run:
            logger.info("\n[DRY RUN MODE] Message preview:")
            self.pusher.push(top_articles, dry_run=True)
        else:
            success = self.pusher.push(top_articles, dry_run=False)
            if success:
                logger.info("✓ News radar completed successfully!")
            else:
                logger.error("✗ News radar completed with push failure.")


def run():
    """外部调用入口"""
    radar = NewsRadar()
    # 默认使用 dry_run=False，实际推送
    radar.run(dry_run=False)


if __name__ == "__main__":
    # 检查是否为测试模式
    import os
    test_mode = os.environ.get("TEST_MODE", "false").lower() == "true"
    
    if test_mode:
        logger.info("🧪 Running in TEST MODE (no actual push)")
        radar = NewsRadar()
        radar.run(dry_run=True)
    else:
        radar = NewsRadar()
        radar.run(dry_run=False)
