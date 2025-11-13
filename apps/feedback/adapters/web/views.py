"""
Vistas web para el módulo de Feedback.
Maneja las peticiones HTTP relacionadas con feedback e historial.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages
from datetime import datetime, timedelta
import json

from ...core.use_cases import (
    SaveFeedbackUseCase,
    GetUserHistoryUseCase,
    FilterHistoryUseCase,
    GetHistoryStatisticsUseCase
)
from ..persistence.repositories import (
    DjangoFeedbackRepository,
    DjangoAnalysisHistoryRepository
)
from ..persistence.models import AnalysisHistoryModel


@login_required
@require_POST
def submit_feedback(request):
    """
    Vista para guardar el feedback de un análisis.
    
    POST params:
        - analysis_id: ID del análisis
        - rating: Calificación (1-5)
        - liked: True/False (opcional)
        - comment: Comentario (opcional)
    """
    try:
        # Obtener datos del formulario
        analysis_id = request.POST.get('analysis_id')
        rating = int(request.POST.get('rating'))
        liked = request.POST.get('liked')
        comment = request.POST.get('comment', '').strip()
        
        # Convertir liked a booleano
        if liked == 'true':
            liked = True
        elif liked == 'false':
            liked = False
        else:
            liked = None
        
        # Validaciones
        if not analysis_id or not rating:
            return JsonResponse({
                'success': False,
                'error': 'Faltan datos requeridos'
            }, status=400)
        
        if not 1 <= rating <= 5:
            return JsonResponse({
                'success': False,
                'error': 'Rating debe estar entre 1 y 5'
            }, status=400)
        
        # Ejecutar caso de uso
        feedback_repo = DjangoFeedbackRepository()
        use_case = SaveFeedbackUseCase(feedback_repo)
        
        feedback = use_case.execute(
            user_id=request.user.id,
            analysis_id=int(analysis_id),
            rating=rating,
            liked=liked,
            comment=comment if comment else None
        )
        
        return JsonResponse({
            'success': True,
            'message': '¡Gracias por tu feedback!',
            'feedback': feedback.to_dict()
        })
        
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Error al guardar el feedback'
        }, status=500)


@login_required
def history_list(request):
    """
    Vista para mostrar el historial de análisis del usuario.
    
    GET params (opcionales):
        - page: Número de página (default: 1)
        - face_shape: Filtrar por forma de rostro
        - min_rating: Filtrar por rating mínimo
        - date_from: Fecha inicial
        - date_to: Fecha final
    """
    # Obtener parámetros de filtrado
    page = int(request.GET.get('page', 1))
    face_shape = request.GET.get('face_shape')
    min_rating = request.GET.get('min_rating')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Configuración de paginación
    items_per_page = 10
    offset = (page - 1) * items_per_page
    
    # Repositorio
    history_repo = DjangoAnalysisHistoryRepository()
    
    # Aplicar filtros si existen
    if any([face_shape, min_rating, date_from, date_to]):
        filter_use_case = FilterHistoryUseCase(history_repo)
        
        if date_from and date_to:
            start_date = datetime.strptime(date_from, '%Y-%m-%d')
            end_date = datetime.strptime(date_to, '%Y-%m-%d')
            history_entries = filter_use_case.filter_by_date(
                request.user.id,
                start_date,
                end_date
            )
        elif face_shape:
            history_entries = filter_use_case.filter_by_face_shape(
                request.user.id,
                face_shape
            )
        elif min_rating:
            history_entries = filter_use_case.filter_by_rating(
                request.user.id,
                int(min_rating)
            )
    else:
        # Sin filtros, obtener historial normal
        history_use_case = GetUserHistoryUseCase(history_repo)
        history_entries = history_use_case.execute(
            request.user.id,
            limit=items_per_page,
            offset=offset
        )
    
    # Obtener estadísticas
    stats_use_case = GetHistoryStatisticsUseCase(history_repo)
    statistics = stats_use_case.execute(request.user.id)
    
    # Calcular paginación
    total_items = history_repo.count_by_user_id(request.user.id)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    context = {
        'history_entries': history_entries,
        'statistics': statistics,
        'current_page': page,
        'total_pages': total_pages,
        'has_previous': page > 1,
        'has_next': page < total_pages,
        'filters': {
            'face_shape': face_shape,
            'min_rating': min_rating,
            'date_from': date_from,
            'date_to': date_to,
        }
    }
    
    return render(request, 'feedback/history_list.html', context)


@login_required
def history_detail(request, history_id):
    """
    Vista para mostrar el detalle de un análisis del historial.
    """
    # Obtener el análisis
    history_repo = DjangoAnalysisHistoryRepository()
    history_entry = history_repo.find_by_id(history_id)
    
    if not history_entry:
        return render(request, '404.html', status=404)
    
    # Verificar que el análisis pertenezca al usuario
    if history_entry.user_id != request.user.id:
        return render(request, '403.html', status=403)
    
    # Parsear los datos JSON
    analysis_data = json.loads(history_entry.analysis_data) if history_entry.analysis_data else {}
    recommendations = json.loads(history_entry.recommendations_data) if history_entry.recommendations_data else {}
    
    # 🆕 OBTENER EL FEEDBACK ASOCIADO
    feedback_repo = DjangoFeedbackRepository()
    feedback = feedback_repo.find_by_analysis_id(history_id)
    
    context = {
        'history_entry': history_entry,
        'analysis_data': analysis_data,
        'recommendations': recommendations,
        'feedback': feedback,  # 🆕 Agregar feedback al contexto
    }
    
    return render(request, 'feedback/history_detail.html', context)


@login_required
def statistics_view(request):
    """
    Vista para mostrar estadísticas del usuario.
    """
    history_repo = DjangoAnalysisHistoryRepository()
    stats_use_case = GetHistoryStatisticsUseCase(history_repo)
    statistics = stats_use_case.execute(request.user.id)
    
    # Datos adicionales para gráficos
    # Análisis por mes (últimos 6 meses)
    six_months_ago = datetime.now() - timedelta(days=180)
    recent_analyses = AnalysisHistoryModel.objects.filter(
        user_id=request.user.id,
        created_at__gte=six_months_ago
    ).order_by('created_at')
    
    # Agrupar por mes
    monthly_data = {}
    for analysis in recent_analyses:
        month_key = analysis.created_at.strftime('%Y-%m')
        monthly_data[month_key] = monthly_data.get(month_key, 0) + 1
    
    context = {
        'statistics': statistics,
        'monthly_data': monthly_data,
    }
    
    return render(request, 'feedback/statistics.html', context)