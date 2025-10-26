from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.recomendations, name='recomendations'),

]