from django.contrib import admin

from apps.auth_app.adapters.persistence.models import UserModel
from django.contrib.auth.admin import UserAdmin
# Register your models here.


@admin.register(UserModel)
class CustomUserAdmin(UserAdmin):
    """Configuración del admin para usuarios personalizados"""

    model = UserModel
    list_display = ('email', 'is_staff', 'is_active', 'created_at')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email',)
    ordering = ('email',)

    # Campos mostrados al ver o editar un usuario
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login',)}),  # ← quitamos created_at y updated_at
    )

    # Campos al crear un nuevo usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
