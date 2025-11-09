import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from collections import Counter
from apps.auth_app.adapters.persistence.models import ProfileModel  # Asegúrate de importar
from apps.recomendations.models import RecommendationModel  # Asegúrate de importar
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
