"""
Configuración del administrador de Django para gestionar estilos.

Ubicación: apps/recomendations/admin.py
"""

from django.contrib import admin
from apps.recomendations.models import (
    HaircutStyleModel,
    BeardStyleModel,
    RecommendationModel
)


@admin.register(HaircutStyleModel)
class HaircutStyleAdmin(admin.ModelAdmin):
    """Admin para estilos de corte de cabello"""
    
    list_display = [
        'name', 
        'difficulty_level', 
        'popularity_score', 
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'difficulty_level',
        'is_active',
        'suitable_for_gender',
        'hair_length_required'
    ]
    
    search_fields = ['name', 'description', 'tags']
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'image_url', 'is_active')
        }),
        ('Compatibilidad', {
            'fields': (
                'suitable_for_shapes',
                'suitable_for_gender',
                'hair_length_required'
            )
        }),
        ('Detalles', {
            'fields': (
                'benefits',
                'tags',
                'difficulty_level',
                'popularity_score'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Mostrar todos los estilos, incluso inactivos"""
        qs = super().get_queryset(request)
        return qs
    
    actions = ['activate_styles', 'deactivate_styles']
    
    def activate_styles(self, request, queryset):
        """Activar estilos seleccionados"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} estilos activados')
    activate_styles.short_description = "Activar estilos seleccionados"
    
    def deactivate_styles(self, request, queryset):
        """Desactivar estilos seleccionados"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} estilos desactivados')
    deactivate_styles.short_description = "Desactivar estilos seleccionados"


@admin.register(BeardStyleModel)
class BeardStyleAdmin(admin.ModelAdmin):
    """Admin para estilos de barba"""
    
    list_display = [
        'name',
        'maintenance_level',
        'popularity_score',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'maintenance_level',
        'is_active',
        'suitable_for_shapes'
    ]
    
    search_fields = ['name', 'description', 'tags']
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'image_url', 'is_active')
        }),
        ('Compatibilidad', {
            'fields': ('suitable_for_shapes',)
        }),
        ('Detalles', {
            'fields': (
                'benefits',
                'tags',
                'maintenance_level',
                'popularity_score'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['activate_styles', 'deactivate_styles']
    
    def activate_styles(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} estilos activados')
    activate_styles.short_description = "Activar estilos seleccionados"
    
    def deactivate_styles(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} estilos desactivados')
    deactivate_styles.short_description = "Desactivar estilos seleccionados"


@admin.register(RecommendationModel)
class RecommendationAdmin(admin.ModelAdmin):
    """Admin para recomendaciones generadas"""
    
    list_display = [
        'id',
        'user_id',
        'face_shape',
        'gender',
        'confidence_score',
        'created_at'
    ]
    
    list_filter = [
        'face_shape',
        'gender',
        'hair_length',
        'created_at'
    ]
    
    search_fields = ['user_id']
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user_id',)
        }),
        ('Análisis', {
            'fields': (
                'face_shape',
                'gender',
                'hair_length',
                'confidence_score'
            )
        }),
        ('Recomendaciones', {
            'fields': (
                'haircut_styles_ids',
                'beard_styles_ids'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        """No permitir crear recomendaciones manualmente"""
        return False