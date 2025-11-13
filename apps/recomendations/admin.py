from django.contrib import admin
from django.utils.safestring import mark_safe
from apps.recomendations.models import (
    HaircutStyleModel,
    BeardStyleModel,
    RecommendationModel
)
from django.db import models

# --- Función Auxiliar ---
# Función para mostrar los datos JSONField en el admin de forma más legible
def display_json_field(obj, field_name):
    """Muestra el contenido de un JSONField como una lista formateada en el admin."""
    data = getattr(obj, field_name, [])
    if data:
        # Crea una lista HTML con los elementos
        html = "<ul>" + "".join([f"<li>{item}</li>" for item in data]) + "</ul>"
        return mark_safe(html)
    return "-"
display_json_field.allow_tags = True
display_json_field.short_description = "Detalle" # Descripción por defecto, se puede cambiar


@admin.register(HaircutStyleModel)
class HaircutStyleAdmin(admin.ModelAdmin):
    """Admin para estilos de corte de cabello"""
    
    # 1. ACTUALIZACIÓN: Añadir 'gender' a la lista de visualización
    list_display = [
        'name',
        'gender',  # 🆕 Nuevo campo
        'difficulty_level', 
        'popularity_score', 
        'is_active',
        'created_at'
    ]
    
    # 2. ACTUALIZACIÓN: Cambiar 'suitable_for_gender' por 'gender' en el filtro
    list_filter = [
        'gender', # 🔄 Usar el campo CharField para filtrar
        'difficulty_level',
        'is_active',
    ]
    
    search_fields = ['name', 'description', 'tags']
    
    # Función para mostrar la imagen en la vista de cambio
    def style_image(self, obj):
        # Asume que el campo se llama 'image' (ImageField)
        if obj.image:
            # Crea un thumbnail de 100px de altura
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 100px;" />')
        return "No Image"
    style_image.short_description = "Imagen"
    
    readonly_fields = ['created_at', 'updated_at', 'style_image'] # 🔄 Añadir 'style_image'
    
    fieldsets = (
        ('Información Básica', {
            # 3. ACTUALIZACIÓN: Cambiar 'image_url' por 'image' y añadir 'style_image' y 'gender'
            'fields': ('name', 'description', 'gender', 'image', 'style_image', 'is_active') 
        }),
        ('Compatibilidad', {
            'fields': (
                'suitable_for_shapes',
                # 'suitable_for_gender', # ❌ Eliminado (usamos el CharField 'gender' en la Info Básica)
                'hair_length_required'
            ),
            # 4. MEJORA: Widgets para JSONField (si necesitas editarlos como texto plano)
            'classes': ('collapse',), 
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
    
    # Muestra los campos JSON como texto plano/lista para edición
    formfield_overrides = {
        models.JSONField: {'widget': admin.widgets.AdminTextareaWidget},
    }
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs
    
    actions = ['activate_styles', 'deactivate_styles']
    
    # ... (Mantener las funciones activate_styles y deactivate_styles)
    def activate_styles(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} estilos activados')
    activate_styles.short_description = "Activar estilos seleccionados"
    
    def deactivate_styles(self, request, queryset):
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
        # No se puede filtrar directamente por contenido de JSONField en list_filter
        # 'suitable_for_shapes' # ❌ Removido, list_filter no funciona bien con JSONField
    ]
    
    search_fields = ['name', 'description', 'tags']
    
    # Función para mostrar la imagen en la vista de cambio (similar a HaircutStyleAdmin)
    def style_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 100px;" />')
        return "No Image"
    style_image.short_description = "Imagen"
    
    readonly_fields = ['created_at', 'updated_at', 'style_image'] # 🔄 Añadir 'style_image'
    
    fieldsets = (
        ('Información Básica', {
            # 🔄 Cambiar 'image_url' por 'image' y añadir 'style_image'
            'fields': ('name', 'description', 'image', 'style_image', 'is_active') 
        }),
        ('Compatibilidad', {
            # 5. MEJORA: Mostrar JSONField como textarea para facilitar la edición
            'fields': ('suitable_for_shapes',),
            'classes': ('collapse',) 
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
    
    # Muestra los campos JSON como texto plano/lista para edición
    formfield_overrides = {
        models.JSONField: {'widget': admin.widgets.AdminTextareaWidget},
    }
    
    actions = ['activate_styles', 'deactivate_styles']
    
    # ... (Mantener las funciones activate_styles y deactivate_styles)
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
    
    # 6. MEJORA: Usar 'user' en lugar de 'user_id' para mostrar el objeto de usuario
    list_display = [
        'id',
        'user', 
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
    
    # 7. MEJORA: Usar la relación (doble guion bajo) para buscar en el usuario
    search_fields = ['user__email', 'user__username', 'face_shape'] 
    
    readonly_fields = [
        'created_at', 
        'updated_at',
        # 8. MEJORA: Añadir métodos para visualizar los IDs de estilos
        'display_haircut_ids', 
        'display_beard_ids'
    ]
    
    # 9. MEJORA: Mostrar los IDs de estilos como texto/lista en el formulario
    def display_haircut_ids(self, obj):
        return display_json_field(obj, 'haircut_styles_ids')
    display_haircut_ids.short_description = "IDs de Cortes Recomendados"

    def display_beard_ids(self, obj):
        return display_json_field(obj, 'beard_styles_ids')
    display_beard_ids.short_description = "IDs de Barbas Recomendadas"

    fieldsets = (
        ('Usuario', {
            # 10. MEJORA: Usar 'user' en lugar de 'user_id'
            'fields': ('user',) 
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
            # 11. MEJORA: Usar los métodos readonly para mostrar los IDs
            'fields': (
                'display_haircut_ids',
                'display_beard_ids'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False