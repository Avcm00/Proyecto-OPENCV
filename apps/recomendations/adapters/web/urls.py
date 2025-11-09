"""
URLs para el módulo de recomendaciones (Django)
"""

from django.urls import path
from . import views

app_name = 'recomendations'

urlpatterns = [
    
    path('haircut-styles/', views.haircuts_list, name='haircuts_list'),
    path('haircut-styles/create/', views.haircut_create, name='haircut_create'),
    path('haircut-styles/<int:pk>/', views.haircut_detail, name='haircut_detail'),
    path('haircut-styles/<int:pk>/edit/', views.haircut_edit, name='haircut_edit'),
    path('haircut-styles/<int:pk>/delete/', views.haircut_delete, name='haircut_delete'),
    
    path('list/', views.recommendations_list, name='recommendations_list'),
    path('recommendations/<int:pk>/', views.recommendation_detail, name='recommendation_detail'),

    path('beard-styles/', views.beard_styles_list, name='beard_styles_list'),
    path('beard-styles/create/', views.beard_style_create, name='beard_style_create'),
    path('beard-styles/<int:pk>/', views.beard_style_detail, name='beard_style_detail'),
    path('beard-styles/<int:pk>/edit/', views.beard_style_edit, name='beard_style_edit'),
    path('beard-styles/<int:pk>/delete/', views.beard_style_delete, name='beard_style_delete'),
]