"""Hacker News API Fetcher"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import hashlib
import requests
from dateutil import parser as date_parser

from config import DATA_SOURCES, SOURCE_WEIGHTS, AI_KEYWORDS

logger = logging.getLogger(__name__)


class HackerNewsFetcher:
    """抓取 Hacker News Top Stories，筛选 AI 相关内容"""
    
    def __init__(self):
        self.source_name = "Hacker News"
        self.api_base = DATA_SOURCES["hackernews"]
        self.weight = SOURCE_WEIGHTS[self.source_name]
        self.keywords = [kw.lower() for kw in AI_KEYWORDS]
    
    def fetch(self) -> List[Dict[str, Any]]:
        """获取 Hacker News Top Stories"""
        logger.info(f"Fetching {self.source_name}...")
        
        articles = []
        try:
            # 获取 Top Stories ID 列表
            top_ids = self._fetch_top_stories(limit=50)
            
            # 获取每个 story 的详情
            for story_id in top_ids:
                try:
                    story = self._fetch_story(story_id)
                    if story and self._is_ai_related(story):
                        article = self._parse_story(story)
                        if article:
                            articles.append(article)
                except Exception as e:
                    logger.warning(f"Failed to fetch story {story_id}: {e}")
                    continue
            
            logger.info(f"✓ {self.source_name}: Fetched {len(articles)} AI-related articles")
            
        except Exception as e:
            logger.error(f"✗ {self.source_name}: Failed to fetch - {e}")
        
        return articles
    
    def _fetch_top_stories(self, limit: int = 50) -> List[int]:
        """获取 Top Stories ID 列表"""
        url = f"{self.api_base}/topstories.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()[:limit]
    
    def _fetch_story(self, story_id: int) -> Dict:
        """获取单个 story 详情"""
        url = f"{self.api_base}/item/{story_id}.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def _is_ai_related(self, story: Dict) -> bool:
        """检查是否与 AI 相关"""
        title = story.get("title", "").lower()
        text = story.get("text", "").lower() if story.get("text") else ""
        
        content = f"{title} {text}"
        return any(keyword in content for keyword in self.keywords)
    
    def _parse_story(self, story: Dict) -> Dict[str, Any]:
        """解析 story 为统一格式"""
        title = story.get("title", "").strip()
        link = story.get("url", f"https://news.ycombinator.com/item?id={story.get('id')}")
        
        if not title:
            return None
        
        story_id = str(story.get("id", ""))
        article_id = hashlib.md5(f"{title}{link}".encode()).hexdigest()[:12]
        
        # 解析发布时间（HN 使用 Unix timestamp）
        time_val = story.get("time")
        if time_val:
            published_at = datetime.utcfromtimestamp(time_val)
        else:
            published_at = datetime.utcnow()
        
        # 获取分数作为热度参考
        score = story.get("score", 0)
        
        return {
            "id": f"hn_{article_id}",
            "title": title,
            "summary": f"Score: {score} points",
            "link": link,
            "source": self.source_name,
            "published_at": published_at.isoformat(),
            "collected_at": datetime.utcnow().isoformat(),
            "hot_score": 0,
            "source_weight": self.weight,
            "hn_score": score,
        }
