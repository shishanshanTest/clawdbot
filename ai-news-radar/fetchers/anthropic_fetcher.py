"""Anthropic Blog RSS Fetcher"""
import logging
from datetime import datetime
from typing import List, Dict, Any
import hashlib
import feedparser
from dateutil import parser as date_parser

from config import DATA_SOURCES, SOURCE_WEIGHTS

logger = logging.getLogger(__name__)


class AnthropicFetcher:
    """抓取 Anthropic Blog RSS 订阅"""
    
    def __init__(self):
        self.source_name = "Anthropic Blog"
        self.rss_url = DATA_SOURCES["anthropic"]
        self.weight = SOURCE_WEIGHTS[self.source_name]
    
    def fetch(self) -> List[Dict[str, Any]]:
        """获取 Anthropic Blog 文章列表"""
        logger.info(f"Fetching {self.source_name}...")
        
        articles = []
        try:
            feed = feedparser.parse(self.rss_url)
            
            for entry in feed.entries:
                try:
                    article = self._parse_entry(entry)
                    if article:
                        articles.append(article)
                except Exception as e:
                    logger.warning(f"Failed to parse entry: {e}")
                    continue
            
            logger.info(f"✓ {self.source_name}: Fetched {len(articles)} articles")
            
        except Exception as e:
            logger.error(f"✗ {self.source_name}: Failed to fetch - {e}")
        
        return articles
    
    def _parse_entry(self, entry) -> Dict[str, Any]:
        """解析单个 RSS entry"""
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        
        if not title or not link:
            return None
        
        article_id = hashlib.md5(f"{title}{link}".encode()).hexdigest()[:12]
        
        published_at = None
        if hasattr(entry, "published"):
            try:
                published_at = date_parser.parse(entry.published)
            except:
                published_at = datetime.utcnow()
        else:
            published_at = datetime.utcnow()
        
        summary = ""
        if hasattr(entry, "summary"):
            summary = entry.summary[:200] + "..." if len(entry.summary) > 200 else entry.summary
        elif hasattr(entry, "description"):
            summary = entry.description[:200] + "..." if len(entry.description) > 200 else entry.description
        
        return {
            "id": f"anthropic_{article_id}",
            "title": title,
            "summary": summary,
            "link": link,
            "source": self.source_name,
            "published_at": published_at.isoformat(),
            "collected_at": datetime.utcnow().isoformat(),
            "hot_score": 0,
            "source_weight": self.weight,
        }
