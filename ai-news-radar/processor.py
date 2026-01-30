"""Data Processor Module - 数据处理（统一格式、去重、热度计算）"""
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Set
from pathlib import Path

from config import RECENCY_BONUS, PROCESSED_DATA_FILE, TOP_N

logger = logging.getLogger(__name__)


class DataProcessor:
    """数据处理类：统一格式、去重、热度计算"""
    
    def __init__(self):
        self.processed_ids: Set[str] = set()
        self._load_processed_data()
    
    def _load_processed_data(self):
        """加载已处理的文章 ID"""
        if PROCESSED_DATA_FILE.exists():
            try:
                with open(PROCESSED_DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.processed_ids = set(data.get("processed_ids", []))
                logger.info(f"Loaded {len(self.processed_ids)} processed article IDs")
            except Exception as e:
                logger.warning(f"Failed to load processed data: {e}")
                self.processed_ids = set()
    
    def _save_processed_data(self):
        """保存已处理的文章 ID"""
        try:
            data = {
                "processed_ids": list(self.processed_ids),
                "updated_at": datetime.utcnow().isoformat()
            }
            with open(PROCESSED_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save processed data: {e}")
    
    def deduplicate(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重：移除已处理和重复的文章"""
        unique_articles = []
        seen_links: Set[str] = set()
        
        for article in articles:
            article_id = article.get("id", "")
            link = article.get("link", "")
            
            # 跳过已处理的文章
            if article_id in self.processed_ids:
                continue
            
            # 跳过相同链接的文章
            if link in seen_links:
                continue
            
            seen_links.add(link)
            unique_articles.append(article)
        
        logger.info(f"Deduplication: {len(articles)} → {len(unique_articles)} articles")
        return unique_articles
    
    def calculate_hot_score(self, article: Dict[str, Any]) -> int:
        """计算热度分数"""
        # 基础权重
        source_weight = article.get("source_weight", 0)
        
        # 时间加成
        recency_bonus = 0
        try:
            published_at = datetime.fromisoformat(article.get("published_at", ""))
            hours_ago = (datetime.utcnow() - published_at).total_seconds() / 3600
            
            if hours_ago <= 1:
                recency_bonus = RECENCY_BONUS.get(1, 20)
            elif hours_ago <= 3:
                recency_bonus = RECENCY_BONUS.get(3, 10)
        except:
            pass
        
        # Hacker News 特殊加成
        hn_bonus = 0
        if "hn_score" in article:
            # 根据 HN score 给予额外加成（每 100 分 +1，最多 +10）
            hn_bonus = min(article["hn_score"] // 100, 10)
        
        total_score = source_weight + recency_bonus + hn_bonus
        return total_score
    
    def process(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """处理文章：去重 + 计算热度 + 排序"""
        if not articles:
            logger.info("No articles to process")
            return []
        
        # 1. 去重
        unique_articles = self.deduplicate(articles)
        
        if not unique_articles:
            logger.info("No new articles after deduplication")
            return []
        
        # 2. 计算热度
        for article in unique_articles:
            article["hot_score"] = self.calculate_hot_score(article)
        
        # 3. 按热度排序
        sorted_articles = sorted(
            unique_articles, 
            key=lambda x: x["hot_score"], 
            reverse=True
        )
        
        # 4. 选取 Top N
        top_articles = sorted_articles[:TOP_N]
        
        # 5. 标记为已处理
        for article in top_articles:
            self.processed_ids.add(article["id"])
        
        # 6. 保存已处理数据
        self._save_processed_data()
        
        logger.info(f"Processed {len(top_articles)} articles (Top {TOP_N})")
        return top_articles
    
    def cleanup_old_data(self, days: int = 7):
        """清理旧数据（可选：定期清理 7 天前的记录）"""
        # 简化版：这里不做复杂清理，实际项目中可以按时间过滤
        pass
