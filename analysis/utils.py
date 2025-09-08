import os
import joblib
import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz
import re
from django.conf import settings
from analysis.models import FinancialNews
from django.conf import settings
BASE_DIR = settings.BASE_DIR


# ✅ Gracefully handle None values
def safe_text(value):
    return value if value is not None else ""


# ✅ Load .pkl models from proper directories
def load_model(model_type, name):
    """
    Loads a model from the 'classification' or 'regression' directory.
    """
    path = os.path.join(BASE_DIR, 'analysis', 'ml', 'model', model_type, f"{name}.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError(f"🚫 Model not found at: {path}")
    print(f"✅ Loaded model: {path}")
    return joblib.load(path)


# ✅ Predict both sentiment and score
def predict_sentiment(text_series, classifier_key):
    print(f"🔍 Loading classifier: {classifier_key}")
    classifier = load_model('classification', classifier_key)

    print("🔍 Loading vectorizer...")
    vectorizer = load_model('classification', 'tfidf_vectorizer')

    print("🔍 Loading regressor...")
    regressor = load_model('regression', 'ridge')

    print("🔍 Transforming text...")
    X = vectorizer.transform(text_series)

    try:
        print("🔍 Predicting sentiment...")
        sentiment = classifier.predict(X)
    except ValueError as e:
        if 'sparse' in str(e).lower():
            print("⚠️ Converting sparse to dense due to error...")
            sentiment = classifier.predict(X.toarray())
        else:
            raise e

    print("🔍 Predicting score...")
    score = regressor.predict(X)

    print("🔍 Loading label encoder...")
    label_encoder = load_model('classification', 'label_encoder')
    sentiment = label_encoder.inverse_transform(sentiment)

    print("📈 Prediction completed.")
    return {'sentiment': sentiment, 'score': score}


# ✅ Load news data from DB or CSV
def load_data_from_source(mode, symbol=None, csv_path=None):
    if mode == 'newsapi_db' and symbol:
        thirty_days_ago = datetime.now(pytz.UTC) - timedelta(days=30)
        queryset = FinancialNews.objects.filter(
            symbol=symbol,
            published_at__gte=thirty_days_ago
        ).order_by('-published_at')

        data = [
            {
                'text': f"{obj.title or ''} {obj.description or ''}",
                'published_at': obj.published_at
            }
            for obj in queryset
        ]
        return pd.DataFrame(data)

    elif mode == 'csv_file' and csv_path:
        return pd.read_csv(csv_path)

    return pd.DataFrame()


# ✅ Fetch news from NewsAPI and store in DB
def fetch_and_store_symbol_news(symbol):
    url = 'https://newsapi.org/v2/everything'
    params = {'q': symbol, 'apiKey': settings.NEWSAPI_KEY}


    try:
        response = requests.get(url, params=params)
        print(f"🔎 NewsAPI response: {response.status_code}, {response.text[:200]}...")
        articles = response.json().get('articles', [])
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching news for {symbol}: {e}")
        return 0

    count = 0
    for article in articles:
        published_at = article.get('publishedAt')
        if not published_at:
            continue

        try:
            published_dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        except Exception as e:
            print(f"❌ Invalid datetime format: {published_at} | Error: {e}")
            continue

        if FinancialNews.objects.filter(symbol=symbol, title=safe_text(article.get('title')), published_at=published_dt).exists():
            continue

        FinancialNews.objects.create(
            symbol=symbol,
            title=safe_text(article.get('title')),
            description=safe_text(article.get('description')),
            content=safe_text(article.get('content')),
            source=safe_text(article.get('source', {}).get('name')),
            published_at=published_dt,
            author=safe_text(article.get('author'))
        )
        count += 1

    return count


def preprocess_text(text, steps=None):
    # Default steps applied if none are provided
    if steps is None:
        steps = ['lowercase', 'remove_html', 'remove_urls', 'remove_special', 'remove_digits']
    if not isinstance(text, str):
        text = str(text)
    if 'lowercase' in steps:
        text = text.lower()
    if 'remove_html' in steps:
        text = re.sub(r"<.*?>", "", text)
    if 'remove_urls' in steps:
        text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    if 'remove_special' in steps:
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    if 'remove_digits' in steps:
        text = re.sub(r'\d+', '', text)
    return text.strip()
