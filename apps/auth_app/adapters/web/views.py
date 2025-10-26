# apps/auth_app/adapters/web/views.py
from django.contrib.auth import login
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, FormView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, render

from apps.auth_app.adapters.persistence.models import UserModel, ProfileModel
from apps.auth_app.adapters.web.forms import RegisterForm, LoginForm, ProfileForm


class RegisterView(CreateView):
    """Vista para registro de nuevos usuarios"""
    model = UserModel
    form_class = RegisterForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('auth:login')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('auth:profile')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            '¡Registro exitoso! Ahora puedes iniciar sesión.'
        )
        return response
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            'Por favor corrige los errores en el formulario.'
        )
        return super().form_invalid(form)


class CustomLoginView(FormView):
    """Vista personalizada para inicio de sesión con email"""
    form_class = LoginForm
    template_name = 'auth/login.html'
    success_url = reverse_lazy('auth:profile')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('auth:profile')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, f'¡Bienvenido/a {user.email}!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            'Email o contraseña incorrectos. Por favor intenta de nuevo.'
        )
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    """Vista personalizada para cerrar sesión"""
    next_page = reverse_lazy('auth:login')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'Has cerrado sesión exitosamente.')
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, View):
    """Vista combinada para ver y editar perfil"""
    template_name = 'auth/profile.html'
    
    def get(self, request):
        profile, created = ProfileModel.objects.get_or_create(user=request.user)
        
        context = {
            'profile': profile,
            'is_complete': profile.is_complete(),
            'stats': {
                'total_analyses': 0,  # Agregar lógica real cuando tengas el modelo de análisis
                'average_precision': 0,
                'average_rating': 0.0
            },
            'history': []  # Agregar lógica real cuando tengas el modelo de análisis
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        profile, created = ProfileModel.objects.get_or_create(user=request.user)
        form = ProfileForm(request.POST, instance=profile)
        
        if form.is_valid():
            form.save()
            messages.success(request, '¡Perfil actualizado exitosamente!')
            return redirect('auth:profile')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
            context = {
                'profile': profile,
                'is_complete': profile.is_complete(),
                'form': form,
                'stats': {
                    'total_analyses': 0,
                    'average_precision': 0,
                    'average_rating': 0.0
                },
                'history': []
            }
            return render(request, self.template_name, context)
        
        
def home(request):
    return render(request, 'home.html')