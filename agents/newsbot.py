"""NewsBot agent for daily news summaries."""

import logging
from datetime import datetime
from typing import Dict, List
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.llm_client import LLMClient
from services.lark_client import LarkClient
from services.news_fetcher import NewsFetcher
from config.settings import settings

logger = logging.getLogger(__name__)


class NewsBot:
    """Agent that fetches and summarizes news, then sends to Lark."""

    def __init__(self, llm_client: LLMClient, lark_client: LarkClient, news_fetcher: NewsFetcher = None):
        """
        Initialize NewsBot.

        Args:
            llm_client: LLM client instance
            lark_client: Lark client instance
            news_fetcher: Optional news fetcher (will create one if not provided)
        """
        self.llm_client = llm_client
        self.lark_client = lark_client
        self.news_fetcher = news_fetcher or NewsFetcher(
            newsapi_key=settings.newsapi_key,
            newsdata_key=settings.newsdata_key
        )
        logger.info("Initialized NewsBot")

    def _fetch_news_headlines(self, category: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Fetch top news headlines from real APIs or fallback to mock.

        Args:
            category: Optional category filter (business, technology, world, etc.)

        Returns:
            List of dicts with 'title', 'source', 'url' keys
        """
        # Try to fetch from real APIs
        preferred_sources = ['reuters', 'bbc-news', 'associated-press', 'scmp', 'hong-kong-free-press']
        
        # Use category if provided
        if category and self.news_fetcher.newsdata_key:
            headlines = self.news_fetcher.fetch_from_newsdata(category=category)
            if headlines:
                logger.info(f"Fetched {len(headlines)} headlines for category: {category}")
                return headlines
        
        headlines = self.news_fetcher.fetch_combined(preferred_sources=preferred_sources)

        # Fallback to mock data if no real news fetched
        if not headlines:
            logger.warning("No real news fetched, using mock data")
            headlines = [
                {
                    "title": "Global Markets Reach New Highs",
                    "source": "Reuters",
                    "url": "https://reuters.com/example1"
                },
                {
                    "title": "Tech Innovation Breakthrough Announced",
                    "source": "BBC",
                    "url": "https://bbc.com/example2"
                },
                {
                    "title": "Climate Summit Reaches Agreement",
                    "source": "AP",
                    "url": "https://apnews.com/example3"
                },
                {
                    "title": "Hong Kong Economic Growth Forecast",
                    "source": "SCMP",
                    "url": "https://scmp.com/example4"
                },
                {
                    "title": "Regional Trade Deal Signed",
                    "source": "HKFP",
                    "url": "https://hongkongfp.com/example5"
                },
            ]

        logger.info(f"Fetched {len(headlines)} news headlines")
        return headlines

    def _summarize_headlines(self, headlines: List[Dict[str, str]]) -> str:
        """
        Summarize headlines using LLM.

        Args:
            headlines: List of headline dicts

        Returns:
            Formatted markdown summary
        """
        # Format headlines for prompt
        headlines_text = "\n".join([
            f"- {h['title']} ({h['source']})"
            for h in headlines
        ])

        prompt = f"""Summarize the following news headlines into a concise daily news summary.

Headlines:
{headlines_text}

Format the summary as markdown with:
- Title: # Daily News Summary - {datetime.now().strftime('%Y-%m-%d')}
- Top Headlines section with 5-10 bullet points
- Categorized sections (World News, Business/Tech, etc.) with 2-4 sentence summaries per story
- Sources list with hyperlinks at the bottom

Keep it factual, neutral, and 600-1200 words total."""

        try:
            summary = self.llm_client.generate(
                prompt=prompt,
                temperature=0.3,
                system_prompt="You are a professional news summarizer. Provide factual, neutral summaries."
            )
            logger.info("Generated news summary")
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {e}", exc_info=True)
            # Fallback summary
            return self._create_fallback_summary(headlines)

    def _create_fallback_summary(self, headlines: List[Dict[str, str]]) -> str:
        """Create a simple fallback summary if LLM fails."""
        date_str = datetime.now().strftime('%Y-%m-%d')
        summary = f"# Daily News Summary - {date_str}\n\n## Top Headlines\n\n"
        for h in headlines:
            summary += f"- {h['title']} ({h['source']})\n"
        summary += "\n## Sources\n\n"
        for h in headlines:
            summary += f"- [{h['title']}]({h['url']}) - {h['source']}\n"
        return summary

    def run(self, category: Optional[str] = None) -> Dict:
        """
        Execute NewsBot workflow.

        Returns:
            Dict with 'success', 'summary', 'headlines_count', 'timestamp' keys
        """
        start_time = datetime.now()
        logger.info("Starting NewsBot run")

        try:
            # Fetch headlines
            headlines = self._fetch_news_headlines(category=category)

            # Summarize
            summary = self._summarize_headlines(headlines)

            # Send to Lark
            date_str = datetime.now().strftime('%Y-%m-%d')
            title = f"Daily News Summary - {date_str}"
            lark_success = self.lark_client.send_markdown(summary, title=title)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            result = {
                "success": lark_success,
                "summary": summary,
                "headlines_count": len(headlines),
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": duration,
            }

            logger.info(f"NewsBot run completed in {duration:.2f}s")
            return result

        except Exception as e:
            logger.error(f"NewsBot run failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
