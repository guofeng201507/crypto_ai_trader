# Crypto News Monitor

A monitoring component that tracks cryptocurrency news from BlockBeats API based on user-defined keywords.

## Features

- **Keyword-based Monitoring**: Track news articles containing specific cryptocurrency terms
- **Real-time Updates**: Continuously checks for new articles at configurable intervals
- **Configurable Keywords**: Monitor relevant terms like 'bitcoin', 'ethereum', 'defi', etc.
- **Multiple Notifications**: Supports console and file logging
- **Deduplication**: Tracks previously seen articles to avoid duplicates
- **Persistent Storage**: Saves new articles to JSON files

## Configuration

The tracker is configured through `config/news_monitor_config.yaml`:

```yaml
# BlockBeats API base URL (update with actual API endpoint)
api_base_url: 'https://api.blockbeats.com'

# API key for BlockBeats (leave empty if no key required)
api_key: ''

# Keywords to monitor in news articles
news_keywords: 
  - 'bitcoin'
  - 'ethereum'
  - 'crypto'
  - 'blockchain'
  - 'defi'
  - 'nft'
  - 'altcoin'
  - 'btc'
  - 'eth'

# How often to check for news (in seconds)
refresh_rate: 300  # 5 minutes

# Directory for storing data
data_dir: 'data/'

# Maximum number of articles to fetch per cycle
max_articles_per_cycle: 20

# Notification methods to use ('console', 'file')
notification_methods: ['console', 'file']
```

## Usage

### Continuous Monitoring
```bash
python -m crypto_news_monitor.main --config config/news_monitor_config.yaml --mode continuous
```

### Single Check
```bash
python -m crypto_news_monitor.main --config config/news_monitor_config.yaml --mode single
```

## Implementation Notes

The current implementation includes a placeholder for the BlockBeats API integration. To use with the real API, you would need to:

1. Obtain API credentials from BlockBeats
2. Update the `fetch_news` method in `news_monitor.py` to make actual API calls
3. Adjust parameters according to BlockBeats API documentation

The structure is designed to be easily adaptable to the actual BlockBeats API once the specific endpoints and parameters are known.

## Data Storage

- Seen article IDs are cached in `data/news_cache.json`
- New articles are saved to `data/crypto_news.json`
- Both files help prevent duplicate processing and maintain history

## Example Output

When new articles are found, the system will output something like:

```
NEW ARTICLE: Bitcoin Reaches New High as Institutional Adoption Grows
URL: https://blockbeats.com/news/bitcoin-institutional-adoption
Relevant Keywords: bitcoin, crypto
```

This component can be integrated with other parts of the crypto trading system to factor in news sentiment when making trading decisions.