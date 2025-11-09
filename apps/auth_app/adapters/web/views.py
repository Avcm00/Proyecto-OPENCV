from django.contrib.auth import login
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, FormView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import Group 
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q

from apps.auth_app.adapters.persistence.models import UserModel, ProfileModel
from apps.auth_app.adapters.web.forms import RegisterForm, LoginForm, ProfileForm


def is_admin(user):
    return user.is_authenticated and user.groups.filter(name='Administrador').exists()

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
        user = form.save()
        
        # Asignar "Usuario" por defecto
        try:
            usuario_group = Group.objects.get(name='Usuario')
            user.groups.add(usuario_group)
            user.save()
        except Group.DoesNotExist:
            print('Warning: Grupo "Usuario" no encontrado. Ejecuta "python manage.py create_default_groups".')
        
        messages.success(self.request, '¡Registro exitoso! Ahora puedes iniciar sesión.')
        return super().form_valid(form)
    
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
        
 # Asegúrate de importar el modelo

@login_required
@user_passes_test(is_admin)
def profiles_list(request):
    profiles = ProfileModel.objects.select_related('user').all().order_by('-created_at')
    
    # Búsqueda por usuario (email o nombre completo)
    query = request.GET.get('q', '')
    if query:
        profiles = profiles.filter(
            Q(user__email__icontains=query) | 
            Q(full_name__icontains=query)
        )
    
    # Filtro por género
    gender_filter = request.GET.get('gender', '')
    if gender_filter:
        profiles = profiles.filter(gender=gender_filter)
    
    # Filtro por forma de cara
    face_shape_filter = request.GET.get('face_shape', '')
    if face_shape_filter:
        profiles = profiles.filter(face_shape=face_shape_filter)
    
    # Paginación
    paginator = Paginator(profiles, 12)  # 12 elementos por página
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    
    # Datos para filtros (géneros y formas de cara únicos)
    genders = ProfileModel.objects.values_list('gender', flat=True).distinct()
    face_shapes = ProfileModel.objects.values_list('face_shape', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'total_count': profiles.count(),
        'query': query,
        'gender_filter': gender_filter,
        'face_shape_filter': face_shape_filter,
        'genders': genders,
        'face_shapes': face_shapes,
    }
    return render(request, 'auth/profiles_list.html', context)

@login_required
@user_passes_test(is_admin)
def profile_detail(request, pk):
    profile = get_object_or_404(ProfileModel.objects.select_related('user'), pk=pk)
    return render(request, 'auth/profile_detail.html', {'profile': profile})

def home(request):
    """
    Vista principal que maneja toda la lógica del dashboard administrativo
    """
    context = {
        'show_sidebar': False,
        'is_admin': False,
        'user_group': None,
    }
    
    # Si el usuario está autenticado, verificar si es administrador
    if request.user.is_authenticated:
        # Obtener grupos del usuario
        user_groups = request.user.groups.all()
        
        if user_groups.exists():
            first_group = user_groups.first()
            context['user_group'] = first_group
            
            # Verificar si pertenece al grupo Administrador
            if first_group.name == 'Administrador':
                context['show_sidebar'] = True
                context['is_admin'] = True
        
        # Información adicional del perfil
        if hasattr(request.user, 'profile'):
            context['profile'] = request.user.profile
            context['profile_complete'] = request.user.profile.is_complete()
    
    # Cambiar 'base.html' por 'home.html'
    return render(request, 'home.html', context)