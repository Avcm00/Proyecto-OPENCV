"""
Vistas (endpoints) para recomendaciones usando Django.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from apps.recomendations.models import HaircutStyleModel, BeardStyleModel, RecommendationModel
from apps.recomendations.adapters.web.forms import HaircutStyleForm, BeardStyleForm
from apps.recomendations.core.use_cases import (
    GenerateHaircutRecommendationsUseCase,
    GenerateBeardRecommendationsUseCase,
    SaveRecommendationUseCase,
    GetRecommendationHistoryUseCase
)
from apps.recomendations.core.entities import (
    Recommendation,
    FaceShape,
    Gender,
    HairLength
)
from apps.recomendations.adapters.persistence.repositories import (
    DjangoRecommendationRepository,
    DjangoStyleRepository
)
from apps.recomendations.adapters.ml.recommendation_engine import (
    RuleBasedRecommendationEngine,
    StyleCatalogServiceImpl
)


# Inicializar dependencias (singleton)
style_repository = DjangoStyleRepository()
recommendation_repository = DjangoRecommendationRepository()
recommendation_engine = RuleBasedRecommendationEngine()
style_catalog = StyleCatalogServiceImpl(style_repository)


@csrf_exempt
@require_http_methods(["POST"])
def generate_admin(request):
    """
    Genera recomendaciones de estilos basadas en el perfil del usuario
    
    POST /recomendations/generate/
    Body: {
        "face_shape": "oval",
        "gender": "hombre",
        "hair_length": "medio",
        "user_id": 1
    }
    """
    try:
        data = json.loads(request.body)
        
        # Validar datos requeridos
        face_shape_str = data.get('face_shape')
        gender_str = data.get('gender', 'hombre')
        hair_length_str = data.get('hair_length', 'medio')
        user_id = data.get('user_id', request.user.id if request.user.is_authenticated else 1)
        
        if not face_shape_str:
            return JsonResponse({
                'error': 'face_shape es requerido'
            }, status=400)
        
        # Convertir strings a enums
        try:
            face_shape = FaceShape(face_shape_str.lower())
            gender = Gender(gender_str.lower())
            hair_length = HairLength(hair_length_str.lower())
        except ValueError as e:
            return JsonResponse({
                'error': f'Valor inválido: {str(e)}'
            }, status=400)
        
        # Generar recomendaciones de corte
        haircut_use_case = GenerateHaircutRecommendationsUseCase(
            recommendation_engine, style_catalog
            )
        haircut_styles = haircut_use_case.execute(
            face_shape=face_shape,
            gender=gender,
            hair_length=hair_length,
            max_results=6
        )
        
        # Generar recomendaciones de barba (solo hombres)
        beard_styles = []
        if gender == Gender.HOMBRE:
            beard_use_case = GenerateBeardRecommendationsUseCase(
                recommendation_engine, style_catalog
                )
            beard_styles = beard_use_case.execute(
                face_shape=face_shape,
                gender=gender,
                max_results=4
            )
        
        # Calcular confidence score
        confidence = 0.0
        if haircut_styles:
            confidence = sum(
                recommendation_engine.calculate_style_score(
                    style, face_shape, gender, hair_length
                )
                for style in haircut_styles
            ) / len(haircut_styles)
        
        # Crear y guardar recomendación
        recommendation = Recommendation(
            user_id=user_id,
            face_shape=face_shape,
            gender=gender,
            hair_length=hair_length,
            haircut_styles=haircut_styles,
            beard_styles=beard_styles,
            confidence_score=confidence
        )
        
        save_use_case = SaveRecommendationUseCase(recommendation_repository)
        saved_recommendation = save_use_case.execute(recommendation)
        
        # Obtener tips
        tips = recommendation_engine.get_face_shape_tips(face_shape)
        
        # Formatear respuesta
        return JsonResponse({
            'success': True,
            'recommendation_id': saved_recommendation.id,
            'face_shape': face_shape.value,
            'confidence_score': confidence,
            'haircut_styles': [
                {
                    'id': style.id,
                    'name': style.name,
                    'description': style.description,
                    'image_url': style.image_url,
                    'benefits': style.benefits,
                    'difficulty_level': style.difficulty_level.value,
                    'popularity_score': style.popularity_score
                }
                for style in haircut_styles
            ],
            'beard_styles': [
                {
                    'id': style.id,
                    'name': style.name,
                    'description': style.description,
                    'image_url': style.image_url,
                    'benefits': style.benefits,
                    'maintenance_level': style.maintenance_level.value
                }
                for style in beard_styles
            ] if beard_styles else [],
            'tips': tips
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error generando recomendaciones: {str(e)}'
        }, status=500)


def is_admin(user):
    return user.is_authenticated and user.groups.filter(name='Administrador').exists()

# ==================== HAIRCUTS VIEWS ====================

@login_required
@user_passes_test(is_admin)
def haircuts_list(request):
    haircuts = HaircutStyleModel.objects.all().order_by('-created_at')
    
    # Búsqueda
    query = request.GET.get('q', '')
    if query:
        haircuts = haircuts.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # Filtro por género
    gender_filter = request.GET.get('gender', '')
    if gender_filter:
        haircuts = haircuts.filter(suitable_for_gender=gender_filter)
    
    # Filtro por longitud de cabello
    length_filter = request.GET.get('length', '')
    if length_filter:
        haircuts = haircuts.filter(hair_length_required=length_filter)
    
    # Paginación
    paginator = Paginator(haircuts, 12)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    
    # Datos para filtros
    genders = HaircutStyleModel.objects.values_list('suitable_for_gender', flat=True).distinct()
    lengths = HaircutStyleModel.objects.values_list('hair_length_required', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'total_count': haircuts.count(),
        'query': query,
        'gender_filter': gender_filter,
        'length_filter': length_filter,
        'genders': genders,
        'lengths': lengths,
    }
    return render(request, 'admin/haircuts_list.html', context)

@login_required
@user_passes_test(is_admin)
def haircut_create(request):
    if request.method == 'POST':
        form = HaircutStyleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Corte de cabello creado exitosamente.')
            return redirect('admin:haircuts_list')
    else:
        form = HaircutStyleForm()
    
    return render(request, 'admin/haircut_form.html', {
        'form': form,
        'title': 'Nuevo Corte de Cabello',
        'button_text': 'Crear Corte'
    })

@login_required
@user_passes_test(is_admin)
def haircut_detail(request, pk):
    haircut = get_object_or_404(HaircutStyleModel, pk=pk)
    return render(request, 'admin/haircut_detail.html', {'haircut': haircut})

@login_required
@user_passes_test(is_admin)
def haircut_edit(request, pk):
    haircut = get_object_or_404(HaircutStyleModel, pk=pk)
    if request.method == 'POST':
        form = HaircutStyleForm(request.POST, request.FILES, instance=haircut)
        if form.is_valid():
            form.save()
            messages.success(request, 'Corte de cabello actualizado exitosamente.')
            return redirect('admin:haircut_detail', pk=pk)
    else:
        form = HaircutStyleForm(instance=haircut)
    
    return render(request, 'admin/haircut_form.html', {
        'form': form,
        'haircut': haircut,
        'title': 'Editar Corte de Cabello',
        'button_text': 'Guardar Cambios'
    })

@login_required
@user_passes_test(is_admin)
def haircut_delete(request, pk):
    haircut = get_object_or_404(HaircutStyleModel, pk=pk)
    if request.method == 'POST':
        haircut.delete()
        messages.success(request, 'Corte de cabello eliminado exitosamente.')
        return redirect('admin:haircuts_list')
    return redirect('admin:haircut_detail', pk=pk)

# ==================== BEARD STYLES VIEWS ====================

@login_required
@user_passes_test(is_admin)
def beard_styles_list(request):
    beard_styles = BeardStyleModel.objects.all().order_by('-created_at')
    
    # Búsqueda
    query = request.GET.get('q', '')
    if query:
        beard_styles = beard_styles.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # Filtro por forma de rostro
    shape_filter = request.GET.get('shape', '')
    if shape_filter:
        beard_styles = beard_styles.filter(suitable_shapes__icontains=shape_filter)
    
    # Filtro por nivel de mantenimiento
    maintenance_filter = request.GET.get('maintenance', '')
    if maintenance_filter:
        beard_styles = beard_styles.filter(maintenance_level=maintenance_filter)
    
    # Paginación
    paginator = Paginator(beard_styles, 12)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    
    # Datos para filtros
    face_shapes = ['Ovalado', 'Redondo', 'Cuadrado', 'Corazón', 'Diamante', 'Triangular']
    maintenance_levels = BeardStyleModel.objects.values_list('maintenance_level', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'total_count': beard_styles.count(),
        'query': query,
        'shape_filter': shape_filter,
        'maintenance_filter': maintenance_filter,
        'face_shapes': face_shapes,
        'maintenance_levels': maintenance_levels,
    }
    return render(request, 'admin/beard_styles_list.html', context)

@login_required
@user_passes_test(is_admin)
def beard_style_create(request):
    if request.method == 'POST':
        form = BeardStyleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Estilo de barba creado exitosamente.')
            return redirect('admin:beard_styles_list')
    else:
        form = BeardStyleForm()
    
    return render(request, 'admin/beard_style_form.html', {
        'form': form,
        'title': 'Nuevo Estilo de Barba',
        'button_text': 'Crear Estilo'
    })

@login_required
@user_passes_test(is_admin)
def beard_style_detail(request, pk):
    beard_style = get_object_or_404(BeardStyleModel, pk=pk)
    return render(request, 'admin/beard_style_detail.html', {'beard_style': beard_style})

@login_required
@user_passes_test(is_admin)
def beard_style_edit(request, pk):
    beard_style = get_object_or_404(BeardStyleModel, pk=pk)
    if request.method == 'POST':
        form = BeardStyleForm(request.POST, request.FILES, instance=beard_style)
        if form.is_valid():
            form.save()
            messages.success(request, 'Estilo de barba actualizado exitosamente.')
            return redirect('admin:beard_style_detail', pk=pk)
    else:
        form = BeardStyleForm(instance=beard_style)
    
    return render(request, 'admin/beard_style_form.html', {
        'form': form,
        'beard_style': beard_style,
        'title': 'Editar Estilo de Barba',
        'button_text': 'Guardar Cambios'
    })

@login_required
@user_passes_test(is_admin)
def beard_style_delete(request, pk):
    beard_style = get_object_or_404(BeardStyleModel, pk=pk)
    if request.method == 'POST':
        beard_style.delete()
        messages.success(request, 'Estilo de barba eliminado exitosamente.')
        return redirect('admin:beard_styles_list')
    return redirect('admin:beard_style_detail', pk=pk)

@login_required
@user_passes_test(is_admin)
def recommendations_list(request):
    recommendations = RecommendationModel.objects.select_related('user__profile').all().order_by('-created_at')
    
    # Búsqueda por usuario (email o nombre completo)
    query = request.GET.get('q', '')
    if query:
        recommendations = recommendations.filter(
            Q(user__email__icontains=query) | 
            Q(user__profile__full_name__icontains=query)
        )
    
    # Filtro por género
    gender_filter = request.GET.get('gender', '')
    if gender_filter:
        recommendations = recommendations.filter(gender=gender_filter)
    
    # Filtro por forma de cara
    face_shape_filter = request.GET.get('face_shape', '')
    if face_shape_filter:
        recommendations = recommendations.filter(face_shape=face_shape_filter)
    
    # Paginación
    paginator = Paginator(recommendations, 12)  # 12 elementos por página
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    
    # Datos para filtros (géneros y formas de cara únicos)
    genders = RecommendationModel.objects.values_list('gender', flat=True).distinct()
    face_shapes = RecommendationModel.objects.values_list('face_shape', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'total_count': recommendations.count(),
        'query': query,
        'gender_filter': gender_filter,
        'face_shape_filter': face_shape_filter,
        'genders': genders,
        'face_shapes': face_shapes,
    }
    return render(request, 'admin/recommendations_list.html', context)

@login_required
@user_passes_test(is_admin)
def recommendation_detail(request, pk):
    recommendation = get_object_or_404(RecommendationModel.objects.select_related('user__profile'), pk=pk)
    return render(request, 'admin/recommendation_detail.html', {'recommendation': recommendation})
