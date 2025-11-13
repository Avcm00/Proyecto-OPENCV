"""
URLs del módulo de Feedback.
"""

from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    # Feedback
    path('submit/', views.submit_feedback, name='submit_feedback'),
    
    # Historial
    path('history/', views.history_list, name='history_list'),
    path('history/<int:history_id>/', views.history_detail, name='history_detail'),
    
    # Estadísticas
    path('statistics/', views.statistics_view, name='statistics'),
]