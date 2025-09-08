

# analysis
from django.core.management.base import BaseCommand
from analysis.models import FinancialNews
import requests
from datetime import datetime
import pytz
import time

NEWS_API_KEY = '077759f74514493185032c0e3ed16a14'

def get_financial_news(symbol):
    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': symbol,
        'apiKey': NEWS_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        articles = response.json().get('articles', [])
        return articles
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching news for {symbol}: {e}")
        return []

class Command(BaseCommand):
    help = 'Fetch financial news and store in the database'

    def handle(self, *args, **kwargs):
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'JPM', 'NVDA', 'V', 'MA', 'DIS']
        pakistan_tz = pytz.timezone('Asia/Karachi')

        for symbol in symbols:
            print(f"📡 Fetching news for {symbol}")
            articles = get_financial_news(symbol)

            count = 0
            for article in articles:
                published_at = article.get('publishedAt')
                if not published_at:
                    continue

                published_dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))

                if FinancialNews.objects.filter(
                    symbol=symbol,
                    title=article.get('title', ''),
                    published_at=published_dt
                ).exists():
                    continue  # skip duplicates

                FinancialNews.objects.create(
                    symbol=symbol,
                    title=article.get('title', ''),
                    description=article.get('description', ''),
                    content=article.get('content', ''),  
                    source=article.get('source', {}).get('name', ''),
                    published_at=published_dt,
                    author=article.get('author', '')
                )
                count += 1

            print(f"✅ Stored {count} new articles for {symbol}")
            time.sleep(1)  # avoid API rate limit
