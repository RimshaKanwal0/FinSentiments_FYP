# models.py within 'base' app

from django.db import models
from django.utils import timezone
from users.models import CustomUser
from .middleware import GlobalRequestMiddleware


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, related_name="%(class)s_created", on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(CustomUser, related_name="%(class)s_updated", on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = GlobalRequestMiddleware.get_current_user()
        if user and not user.is_anonymous:
            if not self.pk:
                self.created_by = user
            self.updated_by = user
        super().save(*args, **kwargs)
