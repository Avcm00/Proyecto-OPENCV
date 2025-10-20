from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.analisis_home, name='analisis_home'),

]