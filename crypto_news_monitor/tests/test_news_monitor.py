"""Unit tests for CryptoNewsMonitor."""
import unittest
from unittest.mock import Mock, patch, mock_open
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from crypto_news_monitor.news_monitor import CryptoNewsMonitor


class TestCryptoNewsMonitor(unittest.TestCase):
    """Test cases for CryptoNewsMonitor."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'api_base_url': 'https://api.test.com',
            'api_key': 'test_key',
            'news_keywords': ['bitcoin', 'ethereum'],
            'refresh_rate': 300,
            'data_dir': self.temp_dir,
            'notification_methods': ['console'],
            'max_articles_per_cycle': 10
        }

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('crypto_news_monitor.news_monitor.NotificationManager', None)
    def test_init(self):
        """Test monitor initialization."""
        monitor = CryptoNewsMonitor()
        self.assertIsNotNone(monitor)
        self.assertIsInstance(monitor.news_cache, set)
        self.assertIsInstance(monitor.news_keywords, list)

    def test_load_config_default(self):
        """Test loading default configuration."""
        monitor = CryptoNewsMonitor()
        config = monitor.config
        self.assertIn('api_base_url', config)
        self.assertIn('news_keywords', config)
        self.assertIn('refresh_rate', config)

    def test_load_news_cache(self):
        """Test loading news cache from file."""
        # Create a cache file
        cache_file = Path(self.temp_dir) / 'news_cache.json'
        test_cache = ['id1', 'id2', 'id3']
        with open(cache_file, 'w') as f:
            json.dump(test_cache, f)
        
        monitor = CryptoNewsMonitor()
        monitor.data_dir = Path(self.temp_dir)
        cache = monitor._load_news_cache()
        
        self.assertIsInstance(cache, set)
        self.assertEqual(len(cache), 3)
        self.assertIn('id1', cache)

    def test_save_news_cache(self):
        """Test saving news cache to file."""
        monitor = CryptoNewsMonitor()
        monitor.data_dir = Path(self.temp_dir)
        monitor.news_cache = {'id1', 'id2', 'id3'}
        
        monitor._save_news_cache()
        
        cache_file = Path(self.temp_dir) / 'news_cache.json'
        self.assertTrue(cache_file.exists())
        
        with open(cache_file, 'r') as f:
            loaded_cache = json.load(f)
        self.assertEqual(len(loaded_cache), 3)

    @patch('crypto_news_monitor.news_monitor.requests.get')
    def test_fetch_news_json_response(self, mock_get):
        """Test fetching news with JSON response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {
            'data': [
                {
                    'id': '1',
                    'title': 'Bitcoin reaches new high',
                    'content': 'Bitcoin price...',
                    'published_at': '2024-01-01T00:00:00Z'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        monitor = CryptoNewsMonitor()
        articles = monitor.fetch_news(['bitcoin'])
        
        self.assertIsInstance(articles, list)
        self.assertGreater(len(articles), 0)

    @patch('crypto_news_monitor.news_monitor.requests.get')
    def test_fetch_news_xml_response(self, mock_get):
        """Test fetching news with XML/RSS response."""
        xml_content = """<?xml version="1.0"?>
        <rss version="2.0">
            <channel>
                <item>
                    <title>Bitcoin News</title>
                    <description>Bitcoin content</description>
                    <link>https://test.com/article</link>
                    <pubDate>Mon, 01 Jan 2024 00:00:00 GMT</pubDate>
                </item>
            </channel>
        </rss>"""
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/xml'}
        mock_response.text = xml_content
        mock_get.return_value = mock_response
        
        monitor = CryptoNewsMonitor()
        articles = monitor.fetch_news(['bitcoin'])
        
        self.assertIsInstance(articles, list)

    def test_filter_news_by_keywords(self):
        """Test filtering news by keywords."""
        monitor = CryptoNewsMonitor()
        monitor.news_keywords = ['bitcoin', 'ethereum']
        
        articles = [
            {
                'id': '1',
                'title': 'Bitcoin reaches ATH',
                'summary': 'Bitcoin price news',
                'content': 'Full content'
            },
            {
                'id': '2',
                'title': 'Stock market update',
                'summary': 'Stocks rising',
                'content': 'No crypto here'
            },
            {
                'id': '3',
                'title': 'Ethereum upgrade',
                'summary': 'ETH news',
                'content': 'Ethereum content'
            }
        ]
        
        filtered = monitor.filter_news_by_keywords(articles)
        self.assertEqual(len(filtered), 2)
        self.assertIn('bitcoin', filtered[0]['title'].lower())

    def test_is_new_article_true(self):
        """Test checking if article is new."""
        monitor = CryptoNewsMonitor()
        monitor.news_cache = {'existing_id'}
        
        article = {'id': 'new_id'}
        result = monitor.is_new_article(article)
        self.assertTrue(result)

    def test_is_new_article_false(self):
        """Test checking if article already exists."""
        monitor = CryptoNewsMonitor()
        monitor.news_cache = {'existing_id'}
        
        article = {'id': 'existing_id'}
        result = monitor.is_new_article(article)
        self.assertFalse(result)

    def test_save_article(self):
        """Test saving article to file."""
        monitor = CryptoNewsMonitor()
        monitor.data_dir = Path(self.temp_dir)
        
        article = {
            'id': 'test_id',
            'title': 'Test Article',
            'summary': 'Test summary',
            'published_at': '2024-01-01T00:00:00Z'
        }
        
        monitor.save_article(article)
        
        news_file = Path(self.temp_dir) / 'crypto_news.json'
        self.assertTrue(news_file.exists())

    @patch('crypto_news_monitor.news_monitor.requests.get')
    def test_process_new_articles(self, mock_get):
        """Test processing new articles."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {
            'data': [
                {
                    'id': 'new_article',
                    'title': 'Bitcoin News',
                    'content': 'Bitcoin reaches new high',
                    'published_at': '2024-01-01T00:00:00Z'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        monitor = CryptoNewsMonitor()
        monitor.data_dir = Path(self.temp_dir)
        monitor.news_cache = set()
        
        new_articles = monitor.process_new_articles()
        
        self.assertIsInstance(new_articles, list)
        self.assertIn('new_article', monitor.news_cache)


if __name__ == '__main__':
    unittest.main()
