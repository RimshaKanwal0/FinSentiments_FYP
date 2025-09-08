from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    path('perform-analysis/', views.perform_analysis, name='perform-analysis'),
    path('results/', views.analysis_result, name='results'),  
    path('stock_symbols/', views.saved_symbols, name='stock_symbols'),
    path('model_gallery/', views.model_gallery, name='model_gallery'),
    path('upload/', views.upload_dataset, name='upload_dataset'),
]
