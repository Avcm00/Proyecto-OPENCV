from django.urls import path, include
from . import views

app_name = 'analysis'

urlpatterns = [
    path('', views.main, name='main'),
    path('results/', views.results, name='results'),
    path('video_feed/', views.video_feed, name='video_feed'),
]