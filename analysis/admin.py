from django.contrib import admin
from .models import ModelArtifact, FinancialNews, NewsAnalysis


@admin.register(ModelArtifact)
class ModelArtifactAdmin(admin.ModelAdmin):
    list_display = ('name', 'accuracy', 'f1_score', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)


@admin.register(FinancialNews)
class FinancialNewsAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'title', 'published_at', 'source', 'author')
    search_fields = ('symbol', 'title', 'source', 'author')
    list_filter = ('symbol', 'published_at')


@admin.register(NewsAnalysis)
class NewsAnalysisAdmin(admin.ModelAdmin):
    list_display = ('user', 'news', 'sentiment', 'score', 'classifier_used')
    search_fields = ('user__username', 'news__symbol', 'sentiment', 'classifier_used')
    list_filter = ('sentiment', 'classifier_used', 'user')
