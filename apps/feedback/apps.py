"""
Configuración de la aplicación Feedback.
"""

from django.apps import AppConfig


class FeedbackConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.feedback'
    verbose_name = 'Sistema de Feedback e Historial'
    
    def ready(self):
        """
        Importar modelos cuando la app esté lista.
        """
        # Importar modelos desde la ubicación personalizada
        from apps.feedback.adapters.persistence import models