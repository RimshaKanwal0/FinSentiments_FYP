from django.db import models
from django.conf import settings 


class ModelArtifact(models.Model):
    name = models.CharField(max_length=100)
    path = models.CharField(max_length=255)
    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} @ {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


class FinancialNews(models.Model):
    symbol = models.CharField(max_length=10)
    title = models.TextField(blank=True)
    description = models.TextField(blank=True)
    content = models.TextField(blank=True)
    source = models.CharField(max_length=255, blank=True)
    published_at = models.DateTimeField()
    author = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.symbol} - {self.published_at.date()}"


class NewsAnalysis(models.Model):
    news = models.ForeignKey(FinancialNews, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    sentiment = models.CharField(max_length=20)
    score = models.FloatField()
    classifier_used = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ('news', 'user')

    def __str__(self):
        return f"{self.user} | {self.news.symbol} | {self.sentiment} | Score: {self.score}"
