
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static


urlpatterns = [
    path('', include('frontend.urls')),  # This will include the URL patterns from the frontend app
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),  # Include URLs from the users app
    path('analysis/', include('analysis.urls')),
    


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
