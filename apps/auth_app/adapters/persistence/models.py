from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin
import uuid


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class UserModel(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255, db_index=True)
    password = models.CharField(max_length=255, db_column='password_hash')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'auth_users'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']

    def __str__(self):
        return self.email

class ProfileModel(models.Model):
    """Modelo Django para Perfil de Usuario"""
    
    GENDER_CHOICES = [
        ('male', 'Masculino'),
        ('female', 'Femenino'),
        ('other', 'Otro'),
        ('prefer_not_to_say', 'Prefiero no decir'),
    ]
    
    FACE_SHAPE_CHOICES = [
        ('oval', 'Ovalado'),
        ('round', 'Redondo'),
        ('square', 'Cuadrado'),
        ('heart', 'Corazón'),
        ('diamond', 'Diamante'),
        ('oblong', 'Oblongo'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        UserModel,
        on_delete=models.CASCADE,
        related_name='profile',
        db_column='user_id'
    )
    full_name = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        null=True,
        blank=True
    )
    height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Altura en metros (ej: 1.75)'
    )
    face_shape = models.CharField(
        max_length=20,
        choices=FACE_SHAPE_CHOICES,
        null=True,
        blank=True,
        help_text='Se detecta automáticamente mediante análisis facial'
    )
    age = models.IntegerField(null=True, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_profiles'
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Perfil de {self.user.email}"
    
    def is_complete(self):
        """Verifica si el perfil está completo"""
        return all([
            self.full_name,
            self.gender,
            self.height,
            self.age
        ])