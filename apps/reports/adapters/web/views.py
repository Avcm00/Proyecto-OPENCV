import json
import os
from django.http import Http404
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from collections import Counter
from Proyecto_OPENCV import settings
from apps.auth_app.adapters.persistence.models import ProfileModel  # Asegúrate de importar
from apps.recomendations.models import RecommendationModel  # Asegúrate de importar

import os
from django.http import FileResponse, JsonResponse, Http404
from django.views import View
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from ...core.use_cases import GeneratePDFReportUseCase
from ...adapters.external.pdf_generator import ReportLabPDFGenerator
# Función para verificar si el usuario es admin
def is_admin(user):
    return user.is_staff or user.is_superuser
# Create your views here.
@login_required
@user_passes_test(is_admin)
def informe(request):
    # 1. Conteo de perfiles por tipo de rostro
    face_shape_counts = dict(
        ProfileModel.objects.values('face_shape').annotate(count=Count('face_shape')).values_list('face_shape', 'count')
    )
    # Asegurar que todos los tipos estén incluidos (incluso si count=0)
    all_shapes = ['oval', 'round', 'square', 'heart', 'diamond', 'oblong']
    face_shape_counts = {shape: face_shape_counts.get(shape, 0) for shape in all_shapes}
    # 2. Top 3 cortes de cabello más repetidos
    haircut_counter = Counter()
    for rec in RecommendationModel.objects.all():
        if rec.haircut_styles_ids:
            ids = json.loads(rec.haircut_styles_ids)
            haircut_counter.update(ids)
    top_haircuts = [{'id': k, 'count': v} for k, v in haircut_counter.most_common(3)]
    # 3. Top 3 barbas más repetidas
    beard_counter = Counter()
    for rec in RecommendationModel.objects.all():
        if rec.beard_styles_ids:
            ids = json.loads(rec.beard_styles_ids)
            beard_counter.update(ids)
    top_beards = [{'id': k, 'count': v} for k, v in beard_counter.most_common(3)]
    context = {
        'face_shape_counts': face_shape_counts,
        'top_haircuts': top_haircuts,
        'top_beards': top_beards,
    }
    return render(request, 'informe.html', context)


class GenerateReportView(View):
    """
    Vista para generar un reporte PDF del análisis facial.
    
    Endpoint: POST /reports/generate/
    
    Body esperado (JSON):
    {
        "user_id": "uuid-string",
        "recommendation_id": 123,
        "analysis": {...},
        "recommendations": {...}
    }
    
    Response:
    {
        "success": true,
        "pdf_url": "/media/reports/analisis_facial_20251107_120000.pdf",
        "download_url": "/reports/download/?file=analisis_facial_20251107_120000.pdf"
    }
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            import json
    
            # Parsear datos del request
            data = json.loads(request.body)
    
            user_id = data.get('user_id', str(request.user.id) if request.user.is_authenticated else '1')
            recommendation_id = data.get('recommendation_id', 0)
            analysis_data = data.get('analysis', {})
            recommendations = data.get('recommendations', {})
    
            # 🧠 Convertir los campos si vienen como JSON string
            if isinstance(analysis_data, str):
                analysis_data = json.loads(analysis_data)
    
            if isinstance(recommendations, str):
                recommendations = json.loads(recommendations)
    
            # Validar datos mínimos
            if not analysis_data or not recommendations:
                return JsonResponse({
                    'success': False,
                    'error': 'Faltan datos del análisis o recomendaciones'
                }, status=400)
    
            # Inicializar dependencias
            pdf_generator = ReportLabPDFGenerator()
            use_case = GeneratePDFReportUseCase(pdf_generator)
    
            # Ejecutar caso de uso
            report = use_case.execute(
                user_id=user_id,
                recommendation_id=recommendation_id,
                analysis_data=analysis_data,
                recommendations=recommendations
            )
    
            # Construir URLs
            pdf_url = f"{settings.MEDIA_URL}{report.pdf_url}"
            filename = os.path.basename(report.pdf_url)
            download_url = f"/reports/download/?file={filename}"
    
            return JsonResponse({
                'success': True,
                'pdf_url': pdf_url,
                'download_url': download_url,
                'filename': filename
            })
    
        except Exception as e:
            print(f"Error generando PDF: {e}")
            import traceback
            traceback.print_exc()
    
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    
    
class DownloadReportView(View):
    """
    Vista para descargar un reporte PDF existente.
    
    Endpoint: GET /reports/download/?file=nombre_archivo.pdf
    
    Response: Archivo PDF para descarga
    """
    
    def get(self, request):
        filename = request.GET.get('file')
        
        if not filename:
            raise Http404("No se especificó archivo")
        
        # Construir ruta completa
        filepath = os.path.join(settings.MEDIA_ROOT, 'reports', filename)
        
        # Verificar que existe
        if not os.path.exists(filepath):
            raise Http404("Archivo no encontrado")
        
        # Retornar archivo como descarga
        response = FileResponse(
            open(filepath, 'rb'),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response