from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponse
import pandas as pd
import csv
from prophet import Prophet
import logging

from .models import FinancialNews, NewsAnalysis, ModelArtifact
from .utils import (
    preprocess_text,
    load_data_from_source,
    predict_sentiment,
    fetch_and_store_symbol_news
)

logger = logging.getLogger(__name__) 


@login_required
def perform_analysis(request):
    forecast_days = int(request.POST.get('forecast_days', 7))

    saved_symbols = NewsAnalysis.objects.filter(user=request.user).values_list('news__symbol', flat=True).distinct()

    # 🔁 Forecast-only update
    if request.method == 'POST' and 'forecast_days' in request.POST and not request.FILES and not request.POST.get('analysis_mode'):
        symbol = request.session.get('last_symbol')
        classifier = request.session.get('last_classifier')
        preprocessing = request.session.get('last_preprocessing', [])
        mode = request.session.get('last_mode')

        if not symbol or not classifier:
            return redirect('perform_analysis')

        df = load_data_from_source('newsapi_db', symbol=symbol)

        if 'published_at' not in df.columns:
            df['published_at'] = [pd.Timestamp.now()] * len(df)

        df['processed'] = df['text'].apply(lambda x: preprocess_text(x, preprocessing)) if preprocessing else df['text']

        result = predict_sentiment(df['processed'], classifier)
        df['sentiment'] = result['sentiment']
        df['score'] = result['score']

        forecast_data = generate_forecast(df, forecast_days)

        output_data = [
            {
                'id': idx + 1,
                'published_at': row.get('published_at', ''),
                'sentiment': row['sentiment'],
                'score': round(row['score'], 2),
                'processed': row.get('processed', '')
            }
            for idx, row in df.tail(14).iterrows()
        ]

        return render(request, 'analysis/results.html', {
            'data': output_data,
            'symbol': symbol,
            'preprocessing': preprocessing,
            'forecast': forecast_data,
            'forecast_days': forecast_days,
            'saved_symbols': saved_symbols,
        })

    # ✅ First-time analysis
    if request.method == 'POST':
        mode = request.POST.get('analysis_mode')
        classifier = request.POST.get('classifier')
        preprocessing = ['lowercase', 'remove_special', 'remove_digits'] if request.POST.get('preprocessing') == 'on' else []

        try:
            if mode == 'newsapi':
                symbol = request.POST.get('symbol')
                df = load_data_from_source('newsapi_db', symbol=symbol)
                if df.empty:
                    fetched = fetch_and_store_symbol_news(symbol)
                    if fetched == 0:
                        return render(request, 'analysis/perform_analysis.html')
                    df = load_data_from_source('newsapi_db', symbol=symbol)
            elif mode == 'upload':
                uploaded_file = request.FILES.get('dataset')
                if not uploaded_file:
                    return render(request, 'analysis/perform_analysis.html')
                df = pd.read_csv(uploaded_file)
                symbol = 'Uploaded Dataset'
            else:
                return render(request, 'analysis/perform_analysis.html')

            if 'published_at' not in df.columns:
                df['published_at'] = [pd.Timestamp.now()] * len(df)

            df['processed'] = df['text'].apply(lambda x: preprocess_text(x, preprocessing)) if preprocessing else df['text']

            result = predict_sentiment(df['processed'], classifier)
            df['sentiment'] = result['sentiment']
            df['score'] = result['score']

            request.session['last_symbol'] = symbol
            request.session['last_classifier'] = classifier
            request.session['last_preprocessing'] = preprocessing
            request.session['last_mode'] = mode
            # ✅ Save only if from NewsAPI
            if mode == 'newsapi':
                articles = FinancialNews.objects.filter(symbol=symbol).order_by('-published_at')
                for idx, row in df.iterrows():
                    try:
                        article = articles[idx]
                        NewsAnalysis.objects.update_or_create(
                            news=article,
                            user=request.user,
                            defaults={
                                'sentiment': row['sentiment'],
                                'score': row['score'],
                                'classifier_used': classifier
                            }
                        )
                    except IndexError:
                        continue

            forecast_data = generate_forecast(df, forecast_days)

            output_data = [
                {
                    'id': idx + 1,
                    'published_at': row.get('published_at', ''),
                    'sentiment': row['sentiment'],
                    'score': round(row['score'], 2),
                    'processed': row.get('processed', '')
                }
                for idx, row in df.tail(14).iterrows()
            ]

            return render(request, 'analysis/results.html', {
                'data': output_data,
                'symbol': symbol,
                'preprocessing': preprocessing,
                'forecast': forecast_data,
                'forecast_days': forecast_days,
                'saved_symbols': saved_symbols,
            })

        except Exception as e:
            logger.error("❌ Error during analysis", exc_info=True)
            return render(request, 'analysis/perform_analysis.html')

    return render(request, 'analysis/perform_analysis.html')


@login_required
def analysis_result(request):
    forecast_days = int(request.POST.get('forecast_days', 7)) if request.method == 'POST' else 7
    selected_symbol = request.POST.get('selected_symbol')

    saved_symbols = NewsAnalysis.objects.filter(user=request.user).values_list('news__symbol', flat=True).distinct()

    if request.method == 'POST' and (selected_symbol or 'forecast_days' in request.POST) and not request.POST.get('analysis_mode'):
        symbol = selected_symbol or request.session.get('last_symbol')
        classifier = request.session.get('last_classifier')
        preprocessing = request.session.get('last_preprocessing', [])

        if not symbol or not classifier:
            logger.warning("Missing symbol or classifier in session for forecast")
            return redirect('perform_analysis')

        analysis_data = NewsAnalysis.objects.filter(news__symbol=symbol, user=request.user).select_related('news').order_by('news__published_at')

        df = pd.DataFrame([
            {
                'published_at': entry.news.published_at,
                'text': entry.news.content or entry.news.description or entry.news.title,
                'sentiment': entry.sentiment,
                'score': entry.score
            } for entry in analysis_data
        ])

        if df.empty:
            logger.info(f"No analysis data found for symbol: {symbol}")
            return render(request, 'analysis/results.html', {
                'data': [],
                'symbol': symbol,
                'forecast': [],
                'forecast_days': forecast_days,
                'saved_symbols': saved_symbols
            })

        df['processed'] = df['text'].apply(lambda x: preprocess_text(x, preprocessing)) if preprocessing else df['text']

        forecast_data = generate_forecast(df, forecast_days)

        output_data = [
            {
                'id': idx + 1,
                'published_at': row.get('published_at', ''),
                'sentiment': row['sentiment'],
                'score': round(row['score'], 2),
                'processed': row.get('processed', '')
            }
            for idx, row in df.tail(14).iterrows()
        ]

        paginator = Paginator(output_data, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request, 'analysis/results.html', {
            'data': page_obj,
            'symbol': symbol,
            'preprocessing': preprocessing,
            'forecast': forecast_data,
            'forecast_days': forecast_days,
            'saved_symbols': saved_symbols
        })

    return render(request, 'analysis/results.html', {
        'data': [],
        'symbol': None,
        'forecast': [],
        'forecast_days': 7,
        'saved_symbols': saved_symbols
    })
# 1️⃣ FORECAST FUNCTION
def generate_forecast(df, days=7):
    try:
        ts_df = df[['published_at', 'score']].copy()
        ts_df.dropna(inplace=True)
        ts_df.rename(columns={'published_at': 'ds', 'score': 'y'}, inplace=True)
        ts_df['ds'] = pd.to_datetime(ts_df['ds']).dt.tz_localize(None)

        model = Prophet()
        model.fit(ts_df)

        future = model.make_future_dataframe(periods=days)
        forecast_df = model.predict(future)

        forecast_points = forecast_df[['ds', 'yhat']].tail(days)
        forecast_data = [
            {'date': row['ds'].strftime('%Y-%m-%d'), 'score': round(row['yhat'], 2)}
            for _, row in forecast_points.iterrows()
        ]
        return forecast_data
    except Exception as e:
        logger.error("❌ Forecasting error", exc_info=True)
        return []
@login_required
def saved_symbols(request):
    symbols = FinancialNews.objects.values_list('symbol', flat=True).distinct()
    results = None
    if request.method == 'POST':
        symbol = request.POST.get('identifier')
        try:
            queryset = NewsAnalysis.objects.select_related('news').filter(
                news__symbol=symbol
            ).order_by('-news__published_at')

            logger.info(f"🔍 User {request.user.id} searched symbol: {symbol}")

            if 'export' in request.POST:
                logger.info(f"📤 User {request.user.id} exported CSV for symbol: {symbol}")

                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="{symbol}_news_analysis.csv"'

                writer = csv.writer(response)
                writer.writerow(['Symbol', 'Title', 'Author', 'Published At', 'Source', 'Sentiment', 'Score'])
                for row in queryset:
                    writer.writerow([
                        row.news.symbol,
                        row.news.title,
                        row.news.author,
                        row.news.published_at.strftime('%Y-%m-%d %H:%M'),
                        row.news.source,
                        row.sentiment,
                        row.score
                    ])

                return response

            results = queryset

        except Exception as e:
            logger.error("❌ Error in saved_symbols view", exc_info=True)

    return render(request, 'analysis/stock_symbols.html', {
        'symbols': symbols,
        'results': results
    })


# 3️⃣ MODEL GALLERY
def model_gallery(request):
    user_info = request.user.id if request.user.is_authenticated else "Anonymous" 
    logger.info(f"📊 User {user_info} accessed model gallery")

    
    models = [
        {
            "name": "Logistic Regression + SGD + SVM",
            "type": "Classifier",
            "accuracy_or_r2": 0.8349,
            "f1_or_rmse": 0.8337,
            "execution_time": 200.33,
            "description": "Blended ensemble of 3 classifiers"
        },
        {
            "name": "SGD",
            "type": "Classifier",
            "accuracy_or_r2": 0.8275,
            "f1_or_rmse": 0.8247,
            "execution_time": 14.13,
            "description": "Fast linear classifier"
        },
        {
            "name": "Logistic Regression + SVM",
            "type": "Classifier",
            "accuracy_or_r2": 0.8237,
            "f1_or_rmse": 0.8231,
            "execution_time": 225.93,
            "description": "Good accuracy with dual model blend"
        },
        {
            "name": "Support Vector Machine",
            "type": "Classifier",
            "accuracy_or_r2": 0.8210,
            "f1_or_rmse": 0.8201,
            "execution_time": 203.69,
            "description": "Effective for high-dimensional data"
        },
        {
            "name": "Ridge Regression",
            "type": "Regressor",
            "accuracy_or_r2": 0.7091,
            "f1_or_rmse": 1.0299,
            "execution_time": 0.42,
            "description": "Regularized linear regression for score prediction"
        },
    ]

    return render(request, 'analysis/model_gallery.html', {'models': models})


# 4️⃣ UPLOAD DATASET
def upload_dataset(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('dataset')
        if uploaded_file:
            try:
                logger.info(f"📁 User {request.user.id if request.user.is_authenticated else 'Anonymous'} uploaded a file: {uploaded_file.name}")

                df = pd.read_csv(uploaded_file)

                if 'text' not in df.columns:
                    logger.warning(f"❌ Missing 'text' column in uploaded file: {uploaded_file.name}")
                    messages.error(request, "❌ 'text' column is required in the uploaded file.")
                    return render(request, 'analysis/upload_dataset.html')

                request.session['uploaded_dataset'] = df.to_dict('records')
                sample_data = df.head(20).to_dict('records')
                messages.success(request, "✅ Dataset uploaded successfully.")
                return render(request, 'analysis/upload.html', {'data': sample_data})

            except Exception as e:
                logger.error("❌ Error reading uploaded CSV file", exc_info=True)
                messages.error(request, "❌ Unable to read the file. Make sure it is a valid CSV.")

    return render(request, 'analysis/upload.html')
