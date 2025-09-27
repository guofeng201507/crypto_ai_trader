"""
Crypto News Monitor using BlockBeats API
Fetches and processes cryptocurrency news based on user-defined keywords
"""
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import json
from loguru import logger
import re


class CryptoNewsMonitor:
    """
    Monitors cryptocurrency news from BlockBeats API
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the crypto news monitor
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self.load_config(config_path)
        
        # Extract configuration values
        self.api_base_url = self.config.get('api_base_url', 'https://api.blockbeats.com')
        self.api_key = self.config.get('api_key', '')
        self.news_keywords = self.config.get('news_keywords', ['crypto', 'bitcoin', 'ethereum'])
        self.refresh_rate = self.config.get('refresh_rate', 300)  # 5 minutes
        self.data_dir = Path(self.config.get('data_dir', 'data/'))
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize cache for tracking seen news
        self.news_cache = self._load_news_cache()
        
        logger.info("Crypto News Monitor initialized")
        logger.info(f"Tracking keywords: {self.news_keywords}")
    
    def load_config(self, config_path: Optional[str] = None) -> Dict:
        """
        Load configuration for the news monitor
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        default_config = {
            'api_base_url': 'https://api.blockbeats.com',
            'api_key': '',
            'news_keywords': ['crypto', 'bitcoin', 'ethereum'],
            'refresh_rate': 300,  # seconds
            'data_dir': 'data/',
            'notification_methods': ['console', 'file'],
            'max_articles_per_cycle': 10
        }
        
        if config_path and Path(config_path).exists():
            try:
                import yaml
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    if user_config:
                        # Update default config with user config, preserving nested structures
                        self._deep_update(default_config, user_config)
            except Exception as e:
                logger.error(f"Could not load config from {config_path}: {e}. Using defaults.")
        
        return default_config
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict):
        """
        Recursively update a nested dictionary
        
        Args:
            base_dict: Base dictionary to update
            update_dict: Dictionary with updates
        """
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def _load_news_cache(self) -> set:
        """
        Load the cache of seen news IDs from file
        
        Returns:
            Set of seen news IDs
        """
        cache_file = self.data_dir / 'news_cache.json'
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    return set(cache_data)
            except Exception as e:
                logger.error(f"Error loading news cache: {e}")
        return set()
    
    def _save_news_cache(self):
        """
        Save the cache of seen news IDs to file
        """
        cache_file = self.data_dir / 'news_cache.json'
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.news_cache), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving news cache: {e}")
    
    def fetch_news(self, keywords: Optional[List[str]] = None) -> List[Dict]:
        """
        Fetch news from the BlockBeats API based on keywords
        
        Args:
            keywords: List of keywords to search for (optional, uses default if not provided)
            
        Returns:
            List of news articles
        """
        if keywords is None:
            keywords = self.news_keywords
        
        # In a real implementation, this would call the BlockBeats API
        # Since we don't know the exact API structure, I'll create a simulated implementation
        # and provide the structure that would work with a real API
        try:
            # This is a placeholder - in a real implementation you would:
            # headers = {
            #     'Authorization': f'Bearer {self.api_key}',
            #     'Content-Type': 'application/json'
            # }
            # params = {
            #     'keywords': ','.join(keywords),
            #     'limit': self.config.get('max_articles_per_cycle', 10)
            # }
            # response = requests.get(f'{self.api_base_url}/news/search', headers=headers, params=params)
            
            # For now, returning sample data structure
            sample_news = [
                {
                    'id': '1',
                    'title': 'Bitcoin Reaches New High as Institutional Adoption Grows',
                    'summary': 'Major financial institutions continue to add Bitcoin to their treasury reserves',
                    'content': 'Full content of the article about Bitcoin and institutional adoption...',
                    'url': 'https://blockbeats.com/news/bitcoin-institutional-adoption',
                    'timestamp': '2025-09-27T22:00:00Z',
                    'source': 'BlockBeats',
                    'tags': ['bitcoin', 'institutional', 'adoption']
                },
                {
                    'id': '2',
                    'title': 'Ethereum 2.0 Upgrade Delivers Promised Improvements',
                    'summary': 'The latest upgrade to Ethereum has increased transaction speed and reduced fees',
                    'content': 'Full content of the article about Ethereum 2.0 upgrades...',
                    'url': 'https://blockbeats.com/news/ethereum-2.0-upgrade',
                    'timestamp': '2025-09-27T21:30:00Z',
                    'source': 'BlockBeats',
                    'tags': ['ethereum', 'upgrade', 'blockchain']
                }
            ]
            
            # Filter sample news based on keywords (in a real implementation, this would be done by the API)
            filtered_news = []
            for article in sample_news:
                title_lower = article['title'].lower()
                summary_lower = article['summary'].lower()
                
                for keyword in keywords:
                    if keyword.lower() in title_lower or keyword.lower() in summary_lower:
                        filtered_news.append(article)
                        break
            
            return filtered_news
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []
    
    def check_for_new_news(self) -> List[Dict]:
        """
        Fetch news and identify new articles not seen before
        
        Returns:
            List of new news articles
        """
        logger.info("Checking for new crypto news...")
        
        articles = self.fetch_news()
        new_articles = []
        
        for article in articles:
            article_id = article.get('id', '')
            if article_id and article_id not in self.news_cache:
                new_articles.append(article)
                self.news_cache.add(article_id)
        
        # Save the updated cache
        self._save_news_cache()
        
        logger.info(f"Found {len(new_articles)} new articles out of {len(articles)} total")
        return new_articles
    
    def process_article(self, article: Dict) -> Dict:
        """
        Process a single news article to extract relevant information
        
        Args:
            article: News article dictionary
            
        Returns:
            Processed article with relevant information
        """
        processed = {
            'id': article.get('id'),
            'title': article.get('title', ''),
            'summary': article.get('summary', ''),
            'url': article.get('url', ''),
            'timestamp': article.get('timestamp', ''),
            'source': article.get('source', ''),
            'tags': article.get('tags', []),
            'processed_at': datetime.now().isoformat(),
            'relevant_keywords': []
        }
        
        # Identify which keywords in the configuration match this article
        for keyword in self.news_keywords:
            title = processed['title'].lower()
            summary = processed['summary'].lower()
            if keyword.lower() in title or keyword.lower() in summary:
                processed['relevant_keywords'].append(keyword)
        
        return processed
    
    def run_monitoring_cycle(self) -> List[Dict]:
        """
        Run one complete monitoring cycle
        
        Returns:
            List of new articles if any are found
        """
        logger.info("Starting news monitoring cycle...")
        
        # Fetch new articles
        new_articles = self.check_for_new_news()
        
        # Process each new article
        processed_articles = []
        for article in new_articles:
            processed_article = self.process_article(article)
            processed_articles.append(processed_article)
        
        logger.info(f"Monitoring cycle completed. Found {len(processed_articles)} new relevant articles.")
        
        return processed_articles
    
    def start_monitoring(self):
        """
        Start the continuous news monitoring process
        """
        logger.info("Starting crypto news monitoring...")
        
        try:
            while True:
                new_articles = self.run_monitoring_cycle()
                
                # Process each new article (could send notifications, etc.)
                for article in new_articles:
                    self.process_new_article(article)
                
                # Wait for refresh interval
                refresh_rate = self.config.get('refresh_rate', 300)
                time.sleep(refresh_rate)
                
        except KeyboardInterrupt:
            logger.info("News monitoring stopped by user")
        except Exception as e:
            logger.error(f"Error in news monitoring loop: {e}")
    
    def process_new_article(self, article: Dict):
        """
        Process a new article (send notification, save, etc.)
        
        Args:
            article: Processed article information
        """
        # Log the new article
        logger.info(f"NEW ARTICLE: {article['title']}")
        logger.info(f"URL: {article['url']}")
        logger.info(f"Relevant Keywords: {', '.join(article['relevant_keywords'])}")
        
        # Additional processing can be added here (notification, etc.)
        notification_methods = self.config.get('notification_methods', ['console'])
        for method in notification_methods:
            if method == 'file':
                self._save_article_to_file(article)
    
    def _save_article_to_file(self, article: Dict):
        """
        Save article to a log file
        
        Args:
            article: Article information dictionary
        """
        articles_file = self.data_dir / "crypto_news.json"
        
        # Read existing articles
        existing_articles = []
        if articles_file.exists():
            try:
                with open(articles_file, 'r', encoding='utf-8') as f:
                    existing_articles = json.load(f)
            except Exception:
                existing_articles = []
        
        # Add new article
        existing_articles.append(article)
        
        # Write back to file (keeping only last 100 articles to prevent file bloat)
        with open(articles_file, 'w', encoding='utf-8') as f:
            json.dump(existing_articles[-100:], f, ensure_ascii=False, indent=2)