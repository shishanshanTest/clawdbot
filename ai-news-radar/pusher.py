"""Feishu Webhook Pusher Module - 飞书 Webhook 推送"""
import json
import logging
from typing import List, Dict, Any
import requests

from config import FEISHU_WEBHOOK_URL, TEST_MODE

logger = logging.getLogger(__name__)


class FeishuPusher:
    """飞书 Webhook 推送类"""
    
    def __init__(self):
        self.webhook_url = FEISHU_WEBHOOK_URL
        self.test_mode = TEST_MODE
    
    def _build_message(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """构建飞书消息体"""
        if not articles:
            return self._build_empty_message()
        
        # 构建消息内容
        content = []
        
        # 标题
        content.append({
            "tag": "text",
            "text": "🔥 每小时 AI 热点 Top 5\n\n"
        })
        
        # 每条资讯
        for i, article in enumerate(articles, 1):
            title = article.get("title", "")
            link = article.get("link", "")
            source = article.get("source", "")
            hot_score = article.get("hot_score", 0)
            
            # 排名 + 标题
            content.append({
                "tag": "text",
                "text": f"{i}. "
            })
            content.append({
                "tag": "a",
                "text": title,
                "href": link
            })
            content.append({
                "tag": "text",
                "text": "\n"
            })
            
            # 来源和热度
            content.append({
                "tag": "text",
                "text": f"   📰 {source}  |  🔥 热度: {hot_score}\n\n"
            })
        
        # 底部提示
        content.append({
            "tag": "text",
            "text": "—\n🤖 AI News Radar | 每小时自动更新"
        })
        
        message = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": "🤖 AI 热点速递（每小时）",
                        "content": [content]
                    }
                }
            }
        }
        
        return message
    
    def _build_empty_message(self) -> Dict[str, Any]:
        """构建无新消息的通知"""
        message = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": "🤖 AI 热点速递（每小时）",
                        "content": [[
                            {
                                "tag": "text",
                                "text": "📭 过去一小时内暂无重大 AI 资讯更新\n\n"
                            },
                            {
                                "tag": "text",
                                "text": "—\n🤖 AI News Radar | 每小时自动更新"
                            }
                        ]]
                    }
                }
            }
        }
        return message
    
    def push(self, articles: List[Dict[str, Any]], dry_run: bool = False) -> bool:
        """推送消息到飞书"""
        if self.test_mode or dry_run:
            logger.info("=" * 50)
            logger.info("[TEST MODE] Would push to Feishu:")
            logger.info("=" * 50)
            self._log_message_preview(articles)
            return True
        
        message = self._build_message(articles)
        
        try:
            logger.info("Pushing message to Feishu...")
            
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") == 0:
                logger.info("✓ Message pushed successfully!")
                return True
            else:
                logger.error(f"✗ Feishu API error: {result}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Failed to push message: {e}")
            # 重试一次
            return self._retry_push(message)
    
    def _retry_push(self, message: Dict[str, Any]) -> bool:
        """重试推送"""
        try:
            logger.info("Retrying push...")
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") == 0:
                logger.info("✓ Message pushed successfully on retry!")
                return True
            else:
                logger.error(f"✗ Retry failed: {result}")
                return False
        except Exception as e:
            logger.error(f"✗ Retry failed: {e}")
            return False
    
    def _log_message_preview(self, articles: List[Dict[str, Any]]):
        """打印消息预览（测试模式）"""
        if not articles:
            logger.info("📭 过去一小时内暂无重大 AI 资讯更新")
            return
        
        logger.info("🤖 AI 热点速递（每小时）")
        logger.info("-" * 40)
        
        for i, article in enumerate(articles, 1):
            logger.info(f"\n{i}. {article.get('title', '')}")
            logger.info(f"   📰 {article.get('source', '')} | 🔥 热度: {article.get('hot_score', 0)}")
            logger.info(f"   🔗 {article.get('link', '')}")
        
        logger.info("\n" + "-" * 40)
        logger.info("🤖 AI News Radar | 每小时自动更新")
