"""
Modelos Django para el sistema de recomendaciones.
"""

from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

from apps.auth_app.adapters.persistence.models import UserModel

class RecommendationModel(models.Model):
    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name='recommendations'
        )
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

from django.db import models
import os

# --- Función Dinámica para Cortes de Cabello ---
def haircut_upload_path(instance, filename):
    """Genera la ruta de subida basada en el género."""
    
    # Normaliza el género a minúsculas para usarlo en la ruta
    gender_folder = instance.gender.lower()
    
    # Define la ruta: styles/haircuts/men/ o styles/haircuts/women/
    return os.path.join(f'styles/haircuts/{gender_folder}/', filename)

DIFFICULTY_CHOICES = [
    ('facil', 'Fácil'),
    ('medio', 'Medio'),
    ('dificil', 'Difícil'),
]
FACE_SHAPE_CHOICES = [
    ('oval', 'Ovalado'),
    ('redondo', 'Redondo'),
    ('cuadrado', 'Cuadrado'),
    ('corazon', 'Corazón'),
    ('diamante', 'Diamante'),
    ('triangular', 'Triangular'),
]

class HaircutStyleModel(models.Model):
    """Modelo para estilos de corte de cabello"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    
    # Campo para definir el género
    GENDER_CHOICES = [
        ('men', 'Hombre'),
        ('women', 'Mujer'),
    ]
    gender = models.CharField(
        max_length=5,
        choices=GENDER_CHOICES,
        default='men', # Asumiendo un default
        help_text="Género al que aplica el estilo (men o women)"
    )
    
    # Usar la función dinámica en upload_to
    image = models.ImageField(upload_to='haircuts/', null=True, blank=True)    
    # ... (El resto del modelo HaircutStyleModel se mantiene igual)
    suitable_for_shapes = models.JSONField(default=list)
    suitable_for_gender = models.JSONField(default=list)
    hair_length_required = models.JSONField(default=list)
    benefits = models.JSONField(default=list)
    tags = models.JSONField(default=list)
    difficulty_level = models.CharField(
        max_length=10, # Suficiente para "dificil"
        choices=DIFFICULTY_CHOICES,
        default='medio',
    )    
    popularity_score = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return None
    

    def save(self, *args, **kwargs):
        # Aquí haces tu lógica personalizada
        # Ejemplo: asegurarte de que el campo JSON esté bien formateado
        if isinstance(self.suitable_for_shapes, list):
            self.suitable_for_shapes = self.suitable_for_shapes

        # Luego guardas normalmente
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BeardStyleModel(models.Model):
    """Modelo para estilos de barba"""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    image = models.ImageField(
        upload_to='beards/',
        null=True,
        blank=True,
        help_text="Imagen del estilo de barba"
    )

    suitable_for_shapes = models.JSONField(
        default=list,
        blank=True,
        help_text="Formas de rostro adecuadas (usa valores como 'oval', 'redondo', 'cuadrado', etc.)"
)    
    benefits = models.JSONField(default=list)
    tags = models.JSONField(default=list)
    difficulty_level = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medio'
    )
    maintenance_level = models.CharField(
        max_length=20,
        default='medio',
        help_text="Nivel de mantenimiento requerido"
    )
    popularity_score = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'beard_styles'
        verbose_name = 'Estilo de Barba'
        verbose_name_plural = 'Estilos de Barba'

    def __str__(self):
        return self.name

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return None
# Y también el HaircutStyleModel y RecommendationModel deben estar presentes y correctos.
# Si estás usando PostgreSQL sin soporte para JSONField nativo en versiones antiguas,
# usa esto en su lugar:
