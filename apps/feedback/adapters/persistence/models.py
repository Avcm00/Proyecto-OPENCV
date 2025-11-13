"""
Modelos Django para el módulo de Feedback.
Representan las tablas en la base de datos.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class FeedbackModel(models.Model):
    """
    Modelo Django para almacenar feedback de usuarios.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        verbose_name='Usuario'
    )
    
    # 🔧 Hacer el campo NULLABLE temporalmente
    analysis_history = models.ForeignKey(
        'AnalysisHistoryModel',
        on_delete=models.CASCADE,
        related_name='feedbacks',
        verbose_name='Historial de Análisis',
        # Eliminar null=True y blank=True
    )
    
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Calificación',
        help_text='Calificación de 1 a 5 estrellas'
    )
    liked = models.BooleanField(
        null=True,
        blank=True,
        verbose_name='Me gusta',
        help_text='True=Like, False=Dislike, None=Sin calificar'
    )
    comment = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Comentario',
        help_text='Comentario opcional del usuario'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )
    
    class Meta:
        db_table = 'feedback_feedbackmodel'
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['analysis_history']),
        ]
    
    def __str__(self):
        user_identifier = (
            getattr(self.user, 'email', None)
            or getattr(self.user, 'full_name', None)
            or f'User {self.user.id}'
        )
        return f"Feedback #{self.id} - {user_identifier} - Rating {self.rating}"




class AnalysisHistoryModel(models.Model):
    """
    Modelo Django para almacenar el historial de análisis faciales.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='facial_analysis_history',
        verbose_name='Usuario'
    )
    face_shape = models.CharField(
        max_length=50,
        verbose_name='Forma de rostro',
        help_text='Forma facial detectada'
    )
    confidence = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        verbose_name='Confianza',
        help_text='Nivel de confianza del análisis (0-100)'
    )
    
    # Datos completos en JSON (para vista detallada)
    analysis_data = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Datos del análisis',
        help_text='Datos completos del análisis en formato JSON'
    )
    recommendations_data = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Datos de recomendaciones',
        help_text='Recomendaciones completas en formato JSON'
    )
    
    recommendations_count = models.IntegerField(
        default=0,
        verbose_name='Cantidad de recomendaciones'
    )
    pdf_path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Ruta del PDF',
        help_text='Ruta relativa del PDF generado'
    )
    
    # 🆕 NUEVO CAMPO PARA LA IMAGEN
    image_path = models.ImageField(
        upload_to='analysis_images/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='Imagen del Análisis'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de análisis'
    )

    class Meta:
        db_table = 'feedback_analysishistorymodel'
        verbose_name = 'Historial de Análisis'
        verbose_name_plural = 'Historial de Análisis'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['face_shape']),
        ]
    def __str__(self):
        created_display = self.created_at.strftime('%Y-%m-%d %H:%M')
        return f"Analysis #{self.id} - {self.user.username} - {created_display}"




    
    @property
    def feedback_rating(self):
        """Retorna el rating del feedback asociado si existe"""
        feedback = self.feedbacks.first()
        return feedback.rating if feedback else None
    
    @property
    def has_feedback(self):
        """Verifica si tiene feedback asociado"""
        return self.feedbacks.exists()