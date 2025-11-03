"""
URLs para el módulo de recomendaciones (Django)
"""

from django.urls import path
from . import views

app_name = 'recomendations'

urlpatterns = [
    # Endpoint para generar recomendaciones
    path('generate/', views.generate_recommendations, name='generate'),
    
    # Endpoint para listar estilos disponibles
    path('styles/', views.list_styles, name='list_styles'),
    path('styles/haircuts/', views.list_haircut_styles, name='list_haircuts'),
    path('styles/beards/', views.list_beard_styles, name='list_beards'),
    
    # Endpoint para obtener detalles de un estilo específico
    path('styles/haircuts/<int:style_id>/', views.get_haircut_detail, name='haircut_detail'),
    path('styles/beards/<int:style_id>/', views.get_beard_detail, name='beard_detail'),
    
    # Endpoint para historial de recomendaciones del usuario
    path('history/', views.get_user_history, name='user_history'),
    path('history/<int:recommendation_id>/', views.get_recommendation_detail, name='recommendation_detail'),
]