"""News fetching service with support for multiple APIs."""

import logging
from typing import List, Dict, Optional
import httpx
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


class NewsFetcher:
    """Fetches news from various APIs."""

    def __init__(self, newsapi_key: Optional[str] = None, newsdata_key: Optional[str] = None):
        """
        Initialize news fetcher.

        Args:
            newsapi_key: NewsAPI.org API key
            newsdata_key: NewsData.io API key
        """
        self.newsapi_key = newsapi_key
        self.newsdata_key = newsdata_key
        logger.info("Initialized NewsFetcher")

    def fetch_from_newsapi(self, sources: List[str] = None, country: str = "hk") -> List[Dict[str, str]]:
        """
        Fetch news from NewsAPI.org.

        Args:
            sources: List of source IDs (e.g., ['reuters', 'bbc-news'])
            country: Country code (default: 'hk' for Hong Kong)

        Returns:
            List of news articles
        """
        if not self.newsapi_key:
            logger.warning("NewsAPI key not configured")
            return []

        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "apiKey": self.newsapi_key,
                "pageSize": 10,
            }

            if sources:
                params["sources"] = ",".join(sources)
            else:
                params["country"] = country

            response = httpx.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            articles = []
            for article in data.get("articles", []):
                if article.get("title") and article.get("url"):
                    articles.append({
                        "title": article["title"],
                        "source": article.get("source", {}).get("name", "Unknown"),
                        "url": article["url"],
                        "description": article.get("description", ""),
                    })

            logger.info(f"Fetched {len(articles)} articles from NewsAPI")
            return articles

        except Exception as e:
            logger.error(f"Error fetching from NewsAPI: {e}", exc_info=True)
            return []

    def fetch_from_newsdata(self, category: str = "top", country: str = "hk") -> List[Dict[str, str]]:
        """
        Fetch news from NewsData.io.

        Args:
            category: News category (top, business, technology, etc.)
            country: Country code (default: 'hk')

        Returns:
            List of news articles
        """
        if not self.newsdata_key:
            logger.warning("NewsData.io key not configured")
            return []

        try:
            url = "https://newsdata.io/api/1/news"
            params = {
                "apikey": self.newsdata_key,
                "category": category,
                "country": country,
                "language": "en",
            }

            response = httpx.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            articles = []
            for article in data.get("results", []):
                if article.get("title") and article.get("link"):
                    articles.append({
                        "title": article["title"],
                        "source": article.get("source_name", "Unknown"),
                        "url": article["link"],
                        "description": article.get("description", ""),
                    })

            logger.info(f"Fetched {len(articles)} articles from NewsData.io")
            return articles

        except Exception as e:
            logger.error(f"Error fetching from NewsData.io: {e}", exc_info=True)
            return []

    def fetch_combined(self, preferred_sources: List[str] = None) -> List[Dict[str, str]]:
        """
        Fetch news from multiple sources and combine.

        Args:
            preferred_sources: Preferred news sources (e.g., ['reuters', 'bbc-news'])

        Returns:
            Combined list of news articles
        """
        all_articles = []

        # Try NewsAPI first
        if self.newsapi_key:
            articles = self.fetch_from_newsapi(sources=preferred_sources)
            all_articles.extend(articles)

        # Try NewsData.io as fallback
        if len(all_articles) < 5 and self.newsdata_key:
            articles = self.fetch_from_newsdata()
            all_articles.extend(articles)

        # Remove duplicates based on title
        seen_titles = set()
        unique_articles = []
        for article in all_articles:
            title_lower = article["title"].lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_articles.append(article)

        logger.info(f"Combined {len(unique_articles)} unique articles")
        return unique_articles[:10]  # Return top 10
