"""GitHub Trending Fetcher"""
import logging
from datetime import datetime
from typing import List, Dict, Any
import hashlib
import requests
from bs4 import BeautifulSoup

from config import DATA_SOURCES, SOURCE_WEIGHTS

logger = logging.getLogger(__name__)


class GitHubFetcher:
    """抓取 GitHub Trending 项目，筛选 AI/ML 相关"""
    
    def __init__(self):
        self.source_name = "GitHub Trending"
        self.url = DATA_SOURCES["github"]
        self.weight = SOURCE_WEIGHTS[self.source_name]
        self.ai_keywords = ["ai", "llm", "gpt", "claude", "model", "machine learning", 
                           "neural", "transformer", "llama", "gemini", "openai", 
                           "anthropic", "stable diffusion", "langchain"]
    
    def fetch(self) -> List[Dict[str, Any]]:
        """获取 GitHub Trending 项目"""
        logger.info(f"Fetching {self.source_name}...")
        
        articles = []
        try:
            # 抓取多个语言分类
            languages = ["", "python", "javascript", "typescript", "jupyter notebook"]
            
            for lang in languages:
                try:
                    repos = self._fetch_trending(lang)
                    for repo in repos:
                        if self._is_ai_related(repo):
                            article = self._parse_repo(repo)
                            if article and not any(a["id"] == article["id"] for a in articles):
                                articles.append(article)
                except Exception as e:
                    logger.warning(f"Failed to fetch trending for {lang}: {e}")
                    continue
            
            logger.info(f"✓ {self.source_name}: Fetched {len(articles)} AI-related repos")
            
        except Exception as e:
            logger.error(f"✗ {self.source_name}: Failed to fetch - {e}")
        
        return articles[:20]  # 限制数量
    
    def _fetch_trending(self, language: str = "") -> List[Dict]:
        """抓取 Trending 页面"""
        url = self.url
        if language:
            url = f"{self.url}/{language.lower().replace(' ', '-')}?since=daily"
        else:
            url = f"{self.url}?since=daily"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        repos = []
        
        # 查找所有 trending repo
        articles = soup.find_all("article", class_="Box-row")
        
        for article in articles:
            try:
                # 获取仓库名
                h2 = article.find("h2")
                if not h2:
                    continue
                
                a_tag = h2.find("a")
                if not a_tag:
                    continue
                
                repo_path = a_tag.get("href", "").strip("/")
                if not repo_path:
                    continue
                
                # 获取描述
                description = ""
                p_tag = article.find("p", class_="col-9")
                if p_tag:
                    description = p_tag.get_text(strip=True)
                
                # 获取 stars 信息
                stars_text = ""
                stars_div = article.find("span", class_="d-inline-block")
                if stars_div:
                    stars_text = stars_div.get_text(strip=True)
                
                repos.append({
                    "name": repo_path,
                    "url": f"https://github.com/{repo_path}",
                    "description": description,
                    "stars_info": stars_text,
                })
            except Exception as e:
                continue
        
        return repos
    
    def _is_ai_related(self, repo: Dict) -> bool:
        """检查是否与 AI 相关"""
        text = f"{repo.get('name', '')} {repo.get('description', '')}".lower()
        return any(keyword in text for keyword in self.ai_keywords)
    
    def _parse_repo(self, repo: Dict) -> Dict[str, Any]:
        """解析 repo 为统一格式"""
        name = repo.get("name", "")
        url = repo.get("url", "")
        description = repo.get("description", "")
        
        if not name:
            return None
        
        article_id = hashlib.md5(f"{name}{url}".encode()).hexdigest()[:12]
        
        title = f"🌟 {name}"
        summary = description[:150] + "..." if len(description) > 150 else description
        if repo.get("stars_info"):
            summary = f"[{repo['stars_info']}] {summary}" if summary else repo['stars_info']
        
        return {
            "id": f"github_{article_id}",
            "title": title,
            "summary": summary,
            "link": url,
            "source": self.source_name,
            "published_at": datetime.utcnow().isoformat(),
            "collected_at": datetime.utcnow().isoformat(),
            "hot_score": 0,
            "source_weight": self.weight,
        }
