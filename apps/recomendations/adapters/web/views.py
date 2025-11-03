"""
Vistas (endpoints) para recomendaciones usando Django.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

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
def generate_recommendations(request):
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


@require_http_methods(["GET"])
def list_styles(request):
    """
    Lista todos los estilos disponibles
    
    GET /recomendations/styles/
    """
    try:
        haircuts = style_repository.get_haircuts()
        beards = style_repository.get_beards()
        
        return JsonResponse({
            'haircuts': [
                {
                    'id': style.id,
                    'name': style.name,
                    'description': style.description,
                    'image_url': style.image_url,
                    'suitable_for_shapes': [shape.value for shape in style.suitable_for_shapes],
                    'popularity_score': style.popularity_score
                }
                for style in haircuts
            ],
            'beards': [
                {
                    'id': style.id,
                    'name': style.name,
                    'description': style.description,
                    'image_url': style.image_url,
                    'suitable_for_shapes': [shape.value for shape in style.suitable_for_shapes],
                    'popularity_score': style.popularity_score
                }
                for style in beards
            ]
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error listando estilos: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def list_haircut_styles(request):
    """
    Lista solo estilos de corte
    
    GET /recomendations/styles/haircuts/
    Query params: ?gender=hombre&hair_length=medio
    """
    try:
        gender_str = request.GET.get('gender')
        hair_length_str = request.GET.get('hair_length')
        
        # Convertir a enums si se proporcionan
        gender = Gender(gender_str.lower()) if gender_str else None
        hair_length = HairLength(hair_length_str.lower()) if hair_length_str else None
        
        haircuts = style_repository.get_haircuts(
            gender=gender,
            hair_length=hair_length
        )
        
        return JsonResponse({
            'haircuts': [
                {
                    'id': style.id,
                    'name': style.name,
                    'description': style.description,
                    'image_url': style.image_url,
                    'suitable_for_shapes': [shape.value for shape in style.suitable_for_shapes],
                    'difficulty_level': style.difficulty_level.value,
                    'popularity_score': style.popularity_score
                }
                for style in haircuts
            ]
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error listando cortes: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def list_beard_styles(request):
    """
    Lista solo estilos de barba
    
    GET /recomendations/styles/beards/
    """
    try:
        beards = style_repository.get_beards()
        
        return JsonResponse({
            'beards': [
                {
                    'id': style.id,
                    'name': style.name,
                    'description': style.description,
                    'image_url': style.image_url,
                    'suitable_for_shapes': [shape.value for shape in style.suitable_for_shapes],
                    'maintenance_level': style.maintenance_level.value,
                    'popularity_score': style.popularity_score
                }
                for style in beards
            ]
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error listando barbas: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def get_haircut_detail(request, style_id):
    """
    Obtiene detalle de un estilo de corte específico
    
    GET /recomendations/styles/haircuts/<id>/
    """
    try:
        style = style_repository.get_haircut_by_id(style_id)
        
        if not style:
            return JsonResponse({
                'error': 'Estilo no encontrado'
            }, status=404)
        
        return JsonResponse({
            'id': style.id,
            'name': style.name,
            'description': style.description,
            'image_url': style.image_url,
            'suitable_for_shapes': [shape.value for shape in style.suitable_for_shapes],
            'suitable_for_gender': [gender.value for gender in style.suitable_for_gender],
            'hair_length_required': [length.value for length in style.hair_length_required],
            'benefits': style.benefits,
            'difficulty_level': style.difficulty_level.value,
            'popularity_score': style.popularity_score,
            'tags': style.tags
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error obteniendo detalle: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def get_beard_detail(request, style_id):
    """
    Obtiene detalle de un estilo de barba específico
    
    GET /recomendations/styles/beards/<id>/
    """
    try:
        style = style_repository.get_beard_by_id(style_id)
        
        if not style:
            return JsonResponse({
                'error': 'Estilo no encontrado'
            }, status=404)
        
        return JsonResponse({
            'id': style.id,
            'name': style.name,
            'description': style.description,
            'image_url': style.image_url,
            'suitable_for_shapes': [shape.value for shape in style.suitable_for_shapes],
            'benefits': style.benefits,
            'maintenance_level': style.maintenance_level.value,
            'popularity_score': style.popularity_score,
            'tags': style.tags
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error obteniendo detalle: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def get_user_history(request):
    """
    Obtiene el historial de recomendaciones del usuario
    
    GET /recomendations/history/
    """
    try:
        user_id = request.GET.get('user_id', request.user.id if request.user.is_authenticated else None)
        
        if not user_id:
            return JsonResponse({
                'error': 'user_id es requerido'
            }, status=400)
        
        limit = int(request.GET.get('limit', 10))
        
        history_use_case = GetRecommendationHistoryUseCase(recommendation_repository)
        recommendations = history_use_case.execute(user_id, limit=limit)
        
        return JsonResponse({
            'recommendations': [
                {
                    'id': rec.id,
                    'face_shape': rec.face_shape.value,
                    'gender': rec.gender.value,
                    'hair_length': rec.hair_length.value,
                    'confidence_score': rec.confidence_score,
                    'created_at': rec.created_at.isoformat() if rec.created_at else None
                }
                for rec in recommendations
            ]
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error obteniendo historial: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def get_recommendation_detail(request, recommendation_id):
    """
    Obtiene detalle de una recomendación específica
    
    GET /recomendations/history/<id>/
    """
    try:
        recommendation = recommendation_repository.get_by_id(recommendation_id)
        
        if not recommendation:
            return JsonResponse({
                'error': 'Recomendación no encontrada'
            }, status=404)
        
        return JsonResponse({
            'id': recommendation.id,
            'user_id': recommendation.user_id,
            'face_shape': recommendation.face_shape.value,
            'gender': recommendation.gender.value,
            'hair_length': recommendation.hair_length.value,
            'confidence_score': recommendation.confidence_score,
            'created_at': recommendation.created_at.isoformat() if recommendation.created_at else None
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error obteniendo recomendación: {str(e)}'
        }, status=500)