"""
Configuración del Django Admin para el módulo Feedback.
"""

from django.contrib import admin
from django.utils.html import format_html
from apps.feedback.adapters.persistence.models import FeedbackModel, AnalysisHistoryModel


@admin.register(FeedbackModel)
class FeedbackAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Feedback.
    """
    list_display = ['id', 'user', 'analysis_history', 'rating', 'liked', 'created_at']  # 👈 Cambié analysis_id por analysis_history
    list_filter = ['rating', 'liked', 'created_at']
    search_fields = [ 'user__email', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('user', 'analysis_history')  # 👈 Cambié analysis_id por analysis_history
        }),
        ('Calificación', {
            'fields': ('rating', 'liked')
        }),
        ('Comentario', {
            'fields': ('comment',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AnalysisHistoryModel)
class AnalysisHistoryAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Historial de Análisis.
    """
    list_display = [
        'id', 
        'user', 
        'face_shape', 
        'confidence', 
        'recommendations_count', 
        'has_image',  # 👈 Nuevo
        'has_feedback', 
        'created_at'
    ]
    list_filter = ['face_shape', 'created_at']
    search_fields = [ 'user__email', 'face_shape']
    readonly_fields = ['created_at', 'image_preview']  # 👈 Agregué image_preview
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información del Análisis', {
            'fields': ('user', 'face_shape', 'confidence', 'recommendations_count')
        }), 
        ('Imagen', {  # 👈 Nueva sección
            'fields': ('image_path', 'image_preview'),
            'classes': ('collapse',)
        }),
        ('Datos Completos (JSON)', {
            'fields': ('analysis_data', 'recommendations_data'),
            'classes': ('collapse',),
            'description': 'Datos en formato JSON para almacenar información completa'
        }),
        ('Archivos', {
            'fields': ('pdf_path',),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_image(self, obj):
        """Indica si tiene imagen asociada."""
        if obj.image_path:
            return format_html(
                '<span style="color: green;">✓ Sí</span>'
            )
        return format_html(
            '<span style="color: red;">✗ No</span>'
        )
    has_image.short_description = 'Tiene Imagen'
    
    def image_preview(self, obj):
        """Muestra preview de la imagen."""
        if obj.image_path:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.image_path.url
            )
        return 'Sin imagen'
    image_preview.short_description = 'Vista Previa'
    
    def has_feedback(self, obj):
        """Indica si tiene feedback asociado."""
        has_fb = obj.feedbacks.exists()
        if has_fb:
            feedback = obj.feedbacks.first()
            stars = '⭐' * feedback.rating
            return format_html(
                '<span title="{} estrellas">{}</span>',
                feedback.rating,
                stars
            )
        return format_html(
            '<span style="color: #999;">Sin calificar</span>'
        )
    has_feedback.short_description = 'Feedback'