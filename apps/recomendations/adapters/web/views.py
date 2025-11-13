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
from apps.auth_app.adapters.persistence.models import ProfileModel
from apps.recomendations.models import HaircutStyleModel, BeardStyleModel, RecommendationModel,FACE_SHAPE_CHOICES, DIFFICULTY_CHOICES
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
        # Actualizar el perfil del usuario con el face_shape detectado, solo si es el mejor puntaje
        try:
            profile = ProfileModel.objects.get(user_id=user_id)
            # Buscar la recomendación con el mayor confidence_score para este usuario
            best_recommendation = RecommendationModel.objects.filter(user_id=user_id).order_by('-confidence_score').first()
            if best_recommendation and best_recommendation.confidence_score >= confidence:
                profile.face_shape = face_shape.value  # Asignar directamente, ya que ahora coinciden
                profile.save()
        except ProfileModel.DoesNotExist:
            # Si no existe perfil, créalo con el face_shape
            ProfileModel.objects.create(user_id=user_id, face_shape=face_shape.value)
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
    query = request.GET.get('q', '').strip()
    gender_filter = request.GET.get('gender', '')
    length_filter = request.GET.get('length', '')

    haircuts = HaircutStyleModel.objects.all()

    # Búsqueda por texto
    if query:
        haircuts = haircuts.filter(name__icontains=query) | haircuts.filter(description__icontains=query)

    # Filtro por género
    if gender_filter:
        haircuts = haircuts.filter(gender=gender_filter)

    # Filtro por longitud (JSONField contiene)
    if length_filter:
        haircuts = haircuts.filter(hair_length_required__icontains=length_filter)

    # Listas de opciones
    gender_choices = HaircutStyleModel.GENDER_CHOICES
    # Para las longitudes, obtén valores únicos del campo JSON
    all_lengths = ["corto", "medio", "largo"]

    # Paginación opcional
    from django.core.paginator import Paginator
    paginator = Paginator(haircuts.order_by('name'), 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
        "gender_filter": gender_filter,
        "length_filter": length_filter,
        "gender_choices": gender_choices,
        "lengths": all_lengths,
        "total_count": haircuts.count(),
    }
    return render(request, "admin/haircuts_list.html", context)
@login_required
@user_passes_test(is_admin)
def haircut_create(request):
    if request.method == 'POST':
        form = HaircutStyleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Corte de cabello creado exitosamente.')
            return redirect('recomendations:haircuts_list')
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
            return redirect('recomendations:haircut_detail', pk=pk)
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
    qs = BeardStyleModel.objects.all().order_by('-created_at')

    query = request.GET.get('q', '').strip()
    if query:
        qs = qs.filter(Q(name__icontains=query) | Q(description__icontains=query))

    # recibimos la key (ej: 'oval')
    shape_filter = request.GET.get('shape', '').strip()
    if shape_filter:
        qs = qs.filter(suitable_for_shapes__contains=[shape_filter])

    difficulty_filter = request.GET.get('difficulty', '').strip()
    if difficulty_filter:
        qs = qs.filter(difficulty_level=difficulty_filter)

    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'total_count': qs.count(),
        'query': query,
        'shape_filter': shape_filter,
        'difficulty_filter': difficulty_filter,
        # pasar choices tal como están (lista de tuplas (key,label))
        'face_shape_choices': FACE_SHAPE_CHOICES,
        'difficulty_choices': DIFFICULTY_CHOICES,
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
            return redirect('recomendations:beard_styles_list')
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
            return redirect('recomendations:beard_style_detail', pk=pk)
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
        return redirect('recomendations:beard_styles_list')
    return redirect('recomendations:beard_style_detail', pk=pk)


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
    
    # 🆕 Enriquecer cada recomendación con los nombres de los estilos
    for rec in recommendations:
        try:
            # Parsear IDs de haircut_styles_ids (viene como JSON string)
            haircut_ids = json.loads(rec.haircut_styles_ids) if rec.haircut_styles_ids else []
            beard_ids = json.loads(rec.beard_styles_ids) if rec.beard_styles_ids else []
            
            # Obtener objetos de estilos
            rec.haircut_styles = HaircutStyleModel.objects.filter(id__in=haircut_ids)
            rec.beard_styles = BeardStyleModel.objects.filter(id__in=beard_ids)
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️ Error al parsear IDs de recomendación {rec.id}: {e}")
            rec.haircut_styles = []
            rec.beard_styles = []
    
    # Paginación
    paginator = Paginator(recommendations, 12)
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
    recommendation = get_object_or_404(
        RecommendationModel.objects.select_related('user__profile'), 
        pk=pk
    )
    
    # 🆕 Obtener los estilos completos con sus nombres e imágenes
    try:
        # Parsear IDs
        haircut_ids = json.loads(recommendation.haircut_styles_ids) if recommendation.haircut_styles_ids else []
        beard_ids = json.loads(recommendation.beard_styles_ids) if recommendation.beard_styles_ids else []
        
        # Obtener objetos completos
        haircut_styles = HaircutStyleModel.objects.filter(id__in=haircut_ids)
        beard_styles = BeardStyleModel.objects.filter(id__in=beard_ids)
        
    except (json.JSONDecodeError, ValueError) as e:
        print(f"⚠️ Error al parsear IDs: {e}")
        haircut_styles = []
        beard_styles = []
    
    context = {
        'recommendation': recommendation,
        'haircut_styles': haircut_styles,
        'beard_styles': beard_styles,
    }
    return render(request, 'admin/recommendation_detail.html', context)