from django.urls import path
from .views import settings_view, success_view

urlpatterns = [
    path('', settings_view, name='settings'),
    path('success/', success_view, name='success'),
]
