from django.test import TestCase

# Create your tests here.
"""
Script de diagnóstico para verificar el sistema de recomendaciones
Ejecutar con: python manage.py shell < debug_recommendations.py
O copiar y pegar en: python manage.py shell
"""

print("=" * 60)
print("DIAGNÓSTICO DEL SISTEMA DE RECOMENDACIONES")
print("=" * 60)

# 1. Verificar modelos
print("\n1. VERIFICANDO MODELOS EN BASE DE DATOS:")
try:
    from apps.recomendations.models import (
        HaircutStyleModel,
        BeardStyleModel,
        RecommendationModel
    )
    
    haircut_count = HaircutStyleModel.objects.count()
    beard_count = BeardStyleModel.objects.count()
    recommendation_count = RecommendationModel.objects.count()
    
    print(f"✓ Cortes de cabello: {haircut_count}")
    print(f"✓ Estilos de barba: {beard_count}")
    print(f"✓ Recomendaciones guardadas: {recommendation_count}")
    
    if haircut_count == 0:
        print("\n⚠️ NO HAY CORTES EN LA BD - Ejecuta: python manage.py populate_styles")
    
    # Mostrar algunos ejemplos
    if haircut_count > 0:
        print("\n  Ejemplos de cortes:")
        for style in HaircutStyleModel.objects.all()[:3]:
            print(f"    - {style.name} (para: {style.suitable_for_shapes})")
    
except Exception as e:
    print(f"✗ Error al verificar modelos: {e}")
    import traceback
    traceback.print_exc()

# 2. Verificar repositorios
print("\n2. VERIFICANDO REPOSITORIOS:")
try:
    from apps.recomendations.adapters.persistence.repositories import (
        DjangoStyleRepository
    )
    from apps.recomendations.core.entities import Gender, HairLength
    
    repo = DjangoStyleRepository()
    
    # Probar obtener cortes
    haircuts = repo.get_haircuts(
        gender=Gender.HOMBRE,
        hair_length=HairLength.MEDIO
    )
    print(f"✓ Repositorio funciona: {len(haircuts)} cortes para hombre/medio")
    
    if len(haircuts) > 0:
        print(f"  Primer corte: {haircuts[0].name}")
    
except Exception as e:
    print(f"✗ Error en repositorio: {e}")
    import traceback
    traceback.print_exc()

# 3. Verificar motor de recomendaciones
print("\n3. VERIFICANDO MOTOR DE RECOMENDACIONES:")
try:
    from apps.recomendations.adapters.ml.recommendation_engine import (
        RuleBasedRecommendationEngine,
        StyleCatalogServiceImpl
    )
    from apps.recomendations.core.entities import FaceShape
    
    engine = RuleBasedRecommendationEngine()
    catalog = StyleCatalogServiceImpl(repo)
    
    # Probar obtener tips
    tips = engine.get_face_shape_tips(FaceShape.OVAL)
    print(f"✓ Motor funciona: {len(tips)} tips para rostro oval")
    print(f"  Tip 1: {tips[0] if tips else 'N/A'}")
    
except Exception as e:
    print(f"✗ Error en motor: {e}")
    import traceback
    traceback.print_exc()

# 4. Verificar casos de uso
print("\n4. VERIFICANDO CASOS DE USO:")
try:
    from apps.recomendations.core.use_cases import (
        GenerateHaircutRecommendationsUseCase
    )
    
    use_case = GenerateHaircutRecommendationsUseCase(engine, catalog)
    recommendations = use_case.execute(
        face_shape=FaceShape.OVAL,
        gender=Gender.HOMBRE,
        hair_length=HairLength.MEDIO,
        max_results=3
    )
    
    print(f"✓ Caso de uso funciona: {len(recommendations)} recomendaciones")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec.name}")
    
except Exception as e:
    print(f"✗ Error en caso de uso: {e}")
    import traceback
    traceback.print_exc()

# 5. Probar mapeo de formas
print("\n5. VERIFICANDO MAPEO DE FORMAS DE ROSTRO:")
try:
    from apps.facial_analysis.adapters.web.views import FACE_SHAPE_MAPPING
    
    test_shapes = ['oval', 'ovalado', 'redondo', 'cuadrado', 'corazón']
    for shape_str in test_shapes:
        mapped = FACE_SHAPE_MAPPING.get(shape_str.lower())
        if mapped:
            print(f"✓ '{shape_str}' → {mapped.value}")
        else:
            print(f"✗ '{shape_str}' → NO MAPEADO")
    
except Exception as e:
    print(f"✗ Error verificando mapeo: {e}")

# 6. Test completo de generación
print("\n6. TEST COMPLETO DE GENERACIÓN:")
try:
    from apps.facial_analysis.adapters.web.views import generate_style_recommendations
    
    test_result = generate_style_recommendations(
        face_shape_str='oval',
        gender_str='hombre',
        hair_length_str='medio',
        user_id=1
    )
    
    if test_result:
        print(f"✓ Generación exitosa!")
        print(f"  Cortes: {len(test_result['cortes'])}")
        print(f"  Barbas: {len(test_result['barba']) if test_result['barba'] else 0}")
        print(f"  Tips: {len(test_result['tips'])}")
        print(f"  Confidence: {test_result['confidence']:.1f}%")
        
        if test_result['cortes']:
            print(f"\n  Top 3 cortes recomendados:")
            for i, corte in enumerate(test_result['cortes'][:3], 1):
                print(f"    {i}. {corte['nombre']}")
    else:
        print("✗ La generación retornó None")
    
except Exception as e:
    print(f"✗ Error en generación completa: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("DIAGNÓSTICO COMPLETADO")
print("=" * 60)