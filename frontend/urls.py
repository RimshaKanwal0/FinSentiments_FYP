from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('submit-contact/', views.submit_contact, name='submit_contact'),
    path('about/', views.about, name='about'), 
    path('reports/', views.reports, name='reports'), 
    path('profile/', views.profile, name='profile'),
]
