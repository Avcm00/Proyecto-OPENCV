# apps/auth_app/adapters/web/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from apps.auth_app.adapters.persistence.models import UserModel, ProfileModel


class RegisterForm(UserCreationForm):
    """Formulario de registro de usuario"""
    email = forms.EmailField(
        max_length=255,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition',
            'placeholder': 'tu@email.com'
        })
    )
    
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition',
            'placeholder': '••••••••'
        })
    )
    
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition',
            'placeholder': '••••••••'
        })
    )
    
    class Meta:
        model = UserModel
        fields = ('email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UserModel.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email ya está registrado.')
        return email.lower()
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            ProfileModel.objects.create(user=user)
        return user


class LoginForm(forms.Form):
    """Formulario de inicio de sesión personalizado usando email"""
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg bg-gray-200 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-yellow-400 focus:bg-white transition',
            'placeholder': 'Enter your Email here',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg bg-gray-200 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-yellow-400 focus:bg-white transition',
            'placeholder': 'Enter your Password here'
        })
    )
    
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)
    
    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        
        if email and password:
            email = email.lower()
            self.user_cache = authenticate(
                self.request,
                username=email,
                password=password
            )
            
            if self.user_cache is None:
                raise forms.ValidationError(
                    'Email o contraseña incorrectos.',
                    code='invalid_login'
                )
        return self.cleaned_data
    
    def get_user(self):
        return self.user_cache


class ProfileForm(forms.ModelForm):
    """Formulario para editar perfil de usuario"""
    
    full_name = forms.CharField(
        max_length=255,
        required=False,
        label='Nombre Completo',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-400 bg-gray-50',
            'placeholder': 'Tu nombre completo'
        })
    )
    
    gender = forms.ChoiceField(
        choices=[('', 'Selecciona tu género')] + ProfileModel.GENDER_CHOICES,
        required=False,
        label='Género',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-400 bg-gray-50'
        })
    )
    
    height = forms.DecimalField(
        required=False,
        min_value=0.5,
        max_value=3.0,
        decimal_places=2,
        label='Altura (metros)',
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-400 bg-gray-50',
            'placeholder': '1.75',
            'step': '0.01'
        })
    )
    
    age = forms.IntegerField(
        required=False,
        min_value=13,
        max_value=120,
        label='Edad',
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-400 bg-gray-50',
            'placeholder': 'años'
        })
    )
    
    class Meta:
        model = ProfileModel
        fields = ['full_name', 'gender', 'height', 'age']
    
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age and age < 13:
            raise forms.ValidationError('Debes tener al menos 13 años.')
        return age
    
    def clean_height(self):
        height = self.cleaned_data.get('height')
        if height and (height < 0.5 or height > 3.0):
            raise forms.ValidationError('La altura debe estar entre 0.5 y 3.0 metros.')
        return height