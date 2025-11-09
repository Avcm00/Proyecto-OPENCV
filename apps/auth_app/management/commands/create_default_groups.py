from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Crea los grupos por defecto: Usuario y Administrador'

    def handle(self, *args, **options):
        # Crear grupo "Usuario" si no existe
        usuario_group, created_usuario = Group.objects.get_or_create(name='Usuario')
        if created_usuario:
            self.stdout.write(self.style.SUCCESS('Grupo "Usuario" creado exitosamente.'))
        else:
            self.stdout.write('Grupo "Usuario" ya existe.')

        # Crear grupo "Administrador" si no existe
        admin_group, created_admin = Group.objects.get_or_create(name='Administrador')
        if created_admin:
            self.stdout.write(self.style.SUCCESS('Grupo "Administrador" creado exitosamente.'))
        else:
            self.stdout.write('Grupo "Administrador" ya existe.')