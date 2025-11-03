"""
Modelos Django para el sistema de recomendaciones.
"""

from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField



# Para versiones de Django < 3.1 sin PostgreSQL
class RecommendationModel(models.Model):
    user_id = models.IntegerField(db_index=True)
    face_shape = models.CharField(max_length=50)
    gender = models.CharField(max_length=20)
    hair_length = models.CharField(max_length=20)
    confidence_score = models.FloatField(default=0.0)
    
    # Usar TextField y serializar/deserializar JSON manualmente
    haircut_styles_ids = models.TextField(default='[]', blank=True)
    beard_styles_ids = models.TextField(default='[]', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'recommendations'
        ordering = ['-created_at']

class HaircutStyleModel(models.Model):
    """Modelo para estilos de corte de cabello"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    image_url = models.URLField(max_length=500)
    
    # Campos como JSON para flexibilidad
    suitable_for_shapes = models.JSONField(
        default=list, 
        help_text="Lista de formas de rostro compatibles"
    )
    suitable_for_gender = models.JSONField(
        default=list,
        help_text="Lista de géneros compatibles"
    )
    hair_length_required = models.JSONField(
        default=list,
        help_text="Longitudes de cabello requeridas"
    )
    benefits = models.JSONField(
        default=list,
        help_text="Beneficios del estilo"
    )
    tags = models.JSONField(
        default=list,
        help_text="Etiquetas del estilo"
    )
    
    # Campos adicionales
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('facil', 'Fácil'),
            ('medio', 'Medio'),
            ('dificil', 'Difícil'),
        ],
        default='medio'
    )
    popularity_score = models.FloatField(default=0.0)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'haircut_styles'
        ordering = ['-popularity_score', 'name']
        indexes = [
            models.Index(fields=['is_active', '-popularity_score']),
        ]
    
    def __str__(self):
        return self.name


class BeardStyleModel(models.Model):
    """Modelo para estilos de barba"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    image_url = models.URLField(max_length=500)
    
    # Campos como JSON
    suitable_for_shapes = models.JSONField(
        default=list,
        help_text="Lista de formas de rostro compatibles"
    )
    benefits = models.JSONField(
        default=list,
        help_text="Beneficios del estilo"
    )
    tags = models.JSONField(
        default=list,
        help_text="Etiquetas del estilo"
    )
    
    # Campos adicionales
    maintenance_level = models.CharField(
        max_length=20,
        choices=[
            ('bajo', 'Bajo'),
            ('medio', 'Medio'),
            ('alto', 'Alto'),
        ],
        default='medio'
    )
    popularity_score = models.FloatField(default=0.0)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'beard_styles'
        ordering = ['-popularity_score', 'name']
        indexes = [
            models.Index(fields=['is_active', '-popularity_score']),
        ]
    
    def __str__(self):
        return self.name


# Si estás usando PostgreSQL sin soporte para JSONField nativo en versiones antiguas,
# usa esto en su lugar:

