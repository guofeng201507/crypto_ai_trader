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
        self.api_base_url = self.config.get('api_base_url', 'https://api.theblockbeats.news')
        self.api_key = self.config.get('api_key', '')
        self.news_keywords = self.config.get('news_keywords', ['crypto', 'bitcoin', 'ethereum'])
        self.refresh_rate = self.config.get('refresh_rate', 300)  # 5 minutes
        self.data_dir = Path(self.config.get('data_dir', 'data/'))
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize cache for tracking seen news
        self.news_cache = self._load_news_cache()
        
        # Initialize notification manager from the price monitor
        try:
            from crypto_price_monitor.notification_manager import NotificationManager
            self.notification_manager = NotificationManager(self.config)
        except ImportError:
            logger.warning("Could not import NotificationManager from price monitor, notifications will be limited")
            self.notification_manager = None
        
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
            'api_base_url': 'https://api.theblockbeats.news',
            'api_key': '',
            'news_keywords': ['crypto', 'bitcoin', 'ethereum'],
            'refresh_rate': 300,  # seconds
            'data_dir': 'data/',
            'notification_methods': ['console', 'file'],
            'max_articles_per_cycle': 10,
            'api_endpoint': '/v2/rss/newsflash'
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
        Fetch flash news from the BlockBeats API
        
        Args:
            keywords: List of keywords to search for (optional, uses default if not provided)
            
        Returns:
            List of news articles
        """
        if keywords is None:
            keywords = self.news_keywords
        
        try:
            # Use the actual BlockBeats flash news API endpoint
            api_endpoint = self.config.get('api_endpoint', '/v2/rss/newsflash')
            url = f"{self.api_base_url}{api_endpoint}"
            
            # Make request to BlockBeats flash news API
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Check the content type to determine how to parse the response
            content_type = response.headers.get('content-type', '').lower()
            
            if 'xml' in content_type or 'rss' in content_type:
                # Parse as XML/RSS
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.text)
                
                articles = []
                
                # Find all items in the RSS feed (standard RSS format)
                for item in root.iter():  # Look for 'item' elements
                    if item.tag.endswith('item') or item.tag.endswith('entry'):
                        article = self._parse_rss_item(item)
                        if article:
                            # Filter based on keywords
                            title_lower = article['title'].lower()
                            summary_lower = article['summary'].lower()
                            
                            # Check if any keyword is in the article
                            keyword_found = False
                            for keyword in keywords:
                                if keyword.lower() in title_lower or keyword.lower() in summary_lower:
                                    keyword_found = True
                                    break
                            
                            if keyword_found:
                                articles.append(article)
            else:
                # Try to parse as JSON
                try:
                    data = response.json()
                    
                    # Extract articles from the response
                    articles = []
                    
                    # Assuming the API returns a list of news items
                    if isinstance(data, list):
                        raw_articles = data
                    elif isinstance(data, dict) and 'data' in data:
                        raw_articles = data['data']
                    else:
                        raw_articles = [data] if data else []
                    
                    for item in raw_articles:
                        # Normalize the structure based on actual BlockBeats API response
                        # This is a template - adjust based on actual response format
                        article = {
                            'id': str(item.get('id', '')) if item.get('id') else str(hash(str(item))),  # Use hash if no ID
                            'title': item.get('title', ''),
                            'summary': item.get('summary', item.get('content', '')),
                            'content': item.get('content', ''),
                            'url': item.get('url', ''),
                            'timestamp': item.get('timestamp', item.get('publish_time', '')),
                            'source': 'BlockBeats',
                            'tags': item.get('tags', []) or []
                        }
                        
                        # Filter based on keywords
                        title_lower = article['title'].lower()
                        summary_lower = article['summary'].lower()
                        
                        # Check if any keyword is in the article
                        keyword_found = False
                        for keyword in keywords:
                            if keyword.lower() in title_lower or keyword.lower() in summary_lower:
                                keyword_found = True
                                break
                        
                        if keyword_found:
                            articles.append(article)
                except ValueError:
                    # If neither XML nor JSON, return empty list
                    logger.error("Could not parse response as XML or JSON")
                    return []
            
            # Limit the number of articles returned
            max_articles = self.config.get('max_articles_per_cycle', 10)
            return articles[:max_articles]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching news: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []
    
    def _parse_rss_item(self, item):
        """
        Parse a single RSS item into article format
        
        Args:
            item: XML element representing an RSS item
            
        Returns:
            Dictionary with article format
        """
        try:
            # Find the specific elements in the RSS item
            title_elem = item.find('.//title')
            desc_elem = item.find('.//description') or item.find('.//summary')
            link_elem = item.find('.//link')
            pubdate_elem = item.find('.//pubDate') or item.find('.//published')
            
            # Extract text content
            title = title_elem.text if title_elem is not None else ''
            description = desc_elem.text if desc_elem is not None else ''
            link = link_elem.text if link_elem is not None else ''
            pub_date = pubdate_elem.text if pubdate_elem is not None else ''
            
            # If link is empty, try to get it from href attribute
            if not link and link_elem is not None:
                link = link_elem.get('href') or link_elem.get('url') or ''
            
            # Parse link from attribute if it's not in text content
            if not link:
                for attr in ['href', 'url', '{http://www.w3.org/1999/xhtml}href']:
                    if link_elem is not None and link_elem.get(attr):
                        link = link_elem.get(attr)
                        break
            
            return {
                'id': str(hash(title + link + pub_date)),  # Create a unique ID based on key fields
                'title': title,
                'summary': description,
                'content': description,  # Same as summary for RSS
                'url': link,
                'timestamp': pub_date,
                'source': 'BlockBeats',
                'tags': []
            }
        except Exception as e:
            logger.error(f"Error parsing RSS item: {e}")
            return None
    
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
        
        # Additional processing can be added here
        notification_methods = self.config.get('notification_methods', ['console'])
        for method in notification_methods:
            if method == 'file':
                self._save_article_to_file(article)
        
        # Send news-specific Telegram notification if configured
        if 'telegram' in notification_methods:
            self._send_news_telegram_alert(article)
    
    def _send_news_telegram_alert(self, article: Dict):\n        \"\"\"\n        Send news alert via Telegram using direct API call with proper news formatting\n        \n        Args:\n            article: Article information\n        \"\"\"\n        import requests\n        \n        bot_token = self.config.get('telegram_bot_token', '')\n        chat_id = self.config.get('telegram_chat_id', '')\n        \n        if not bot_token or not chat_id:\n            logger.warning(\"Telegram bot token or chat ID not configured, skipping Telegram alert\")\n            return\n        \n        try:\n            # Ensure chat_id is properly formatted\n            try:\n                if isinstance(chat_id, str) and chat_id.lstrip('-').isdigit():\n                    chat_id = int(chat_id)\n            except ValueError:\n                pass\n            \n            telegram_url = f\"https://api.telegram.org/bot{bot_token}/sendMessage\"\n            \n            # Create news-specific message with proper formatting\n            title = article['title']\n            url = article['url']\n            keywords = ', '.join(article['relevant_keywords'])\n            \n            message = (\n                f\"*🚨 Crypto News Alert 🚨*\\n\\n\"\n                f\"*Keywords:* {keywords}\\n\"\n                f\"*Title:* {title}\\n\"\n                f\"*URL:* {url}\\n\"\n                f\"*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\"\n            )\n            \n            payload = {\n                'chat_id': chat_id,\n                'text': message,\n                'parse_mode': 'Markdown'\n            }\n            \n            response = requests.post(telegram_url, json=payload)\n            response.raise_for_status()\n            \n            logger.info(\"News Telegram alert sent successfully\")\n        except Exception as e:\n            logger.error(f\"Failed to send news Telegram alert: {e}\")\n
    
    def _send_custom_telegram_message(self, article: Dict):
        """
        Send custom Telegram message for news alerts using direct API call
        
        Args:
            article: Article information
        """
        import requests
        
        bot_token = self.config.get('telegram_bot_token', '')
        chat_id = self.config.get('telegram_chat_id', '')
        
        if not bot_token or not chat_id:
            logger.warning("Telegram bot token or chat ID not configured, skipping Telegram alert")
            return
        
        try:
            # Ensure chat_id is properly formatted
            try:
                if isinstance(chat_id, str) and chat_id.lstrip('-').isdigit():
                    chat_id = int(chat_id)
            except ValueError:
                pass
            
            telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            # Create news-specific message
            title = article['title']
            url = article['url']
            keywords = ', '.join(article['relevant_keywords'])
            
            message = (
                f"*🚨 Crypto News Alert 🚨*\n\n"
                f"*Keywords:* {keywords}\n"
                f"*Title:* {title}\n"
                f"*URL:* {url}\n"
                f"*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(telegram_url, json=payload)
            response.raise_for_status()
            
            logger.info("News Telegram alert sent successfully via fallback method")
        except Exception as e:
            logger.error(f"Failed to send news Telegram alert via fallback method: {e}")
    
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