import datetime,json,time,traceback,cv2
from celery import uuid
from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse, HttpResponse
from django.views.decorators import gzip
from apps.auth_app.adapters.persistence.models import ProfileModel
from apps.facial_analysis.face_shape_detection import FaceShapeDetector
from apps.facial_analysis.ml.face_shape_classifier import FaceShapeClassifier
from django.core.files.base import ContentFile
import numpy as np

from apps.feedback.core.entities import AnalysisHistory
from apps.recomendations.core.use_cases import (
    GenerateHaircutRecommendationsUseCase,
    GenerateBeardRecommendationsUseCase,
    SaveRecommendationUseCase
)
from apps.recomendations.core.entities import (
    Recommendation, FaceShape, Gender, HairLength
)
from apps.recomendations.adapters.persistence.repositories import (
    DjangoRecommendationRepository,
    DjangoStyleRepository
)
from apps.recomendations.adapters.ml.recommendation_engine import (
    RuleBasedRecommendationEngine,
    StyleCatalogServiceImpl
)
from apps.feedback.adapters.persistence.repositories import DjangoAnalysisHistoryRepository

# Inicializar dependencias de recomendaciones (una vez)
style_repository = DjangoStyleRepository()
recommendation_repository = DjangoRecommendationRepository()
recommendation_engine = RuleBasedRecommendationEngine()
style_catalog = StyleCatalogServiceImpl(style_repository)
stop_camera = False  # Bandera global para detener la cámara
# 🆕 Inicializar repositorio de historial
history_repository = DjangoAnalysisHistoryRepository()

# Mapeo de formas de rostro en español a enums
FACE_SHAPE_MAPPING = {
    'oval': FaceShape.OVAL,
    'ovalada': FaceShape.OVAL,
    'redonda': FaceShape.REDONDO,
    'cuadrada': FaceShape.CUADRADO,
    'corazón': FaceShape.CORAZON,
    'corazon': FaceShape.CORAZON,
    'diamante': FaceShape.DIAMANTE,
    'triangular': FaceShape.TRIANGULAR,
}

def debug_database_content():
    """Función de debugging para verificar contenido de BD"""
    from apps.recomendations.models import HaircutStyleModel, BeardStyleModel
    
    print("\n" + "="*80)
    print("🔍 DEBUG: CONTENIDO DE BASE DE DATOS")
    print("="*80)
    
    # 1. Contar total de estilos
    total_haircuts = HaircutStyleModel.objects.count()
    total_beards = BeardStyleModel.objects.count()
    print(f"📊 Total estilos de corte: {total_haircuts}")
    print(f"📊 Total estilos de barba: {total_beards}")
    
    # 2. Ver géneros disponibles
    haircut_genders = HaircutStyleModel.objects.values_list('gender', flat=True).distinct()
    print(f"👥 Géneros en HaircutStyleModel: {list(haircut_genders)}")
    
    # 3. Ver formas de rostro disponibles
    print(f"\n📋 Primeros 5 estilos con sus formas compatibles:")
    for style in HaircutStyleModel.objects.all()[:5]:
        print(f"   - {style.name}:")
        print(f"     Gender: {style.gender}")
        print(f"     Suitable shapes: {style.suitable_for_shapes}")
        print(f"     Hair lengths: {style.hair_length_required}")
    
    # 4. Buscar estilos para 'cuadrado' + 'male'
    print(f"\n🔎 Buscando estilos para face_shape='cuadrado' y gender='male':")
    
    # Intento 1: Búsqueda exacta
    from django.db.models import Q
    estilos_male = HaircutStyleModel.objects.filter(
        gender='male',
        suitable_for_shapes__contains=['cuadrado']
    )
    print(f"   Método 1 (gender='male'): {estilos_male.count()} resultados")
    
    # Intento 2: Búsqueda alternativa
    estilos_men = HaircutStyleModel.objects.filter(
        gender='men',
        suitable_for_shapes__contains=['cuadrado']
    )
    print(f"   Método 2 (gender='men'): {estilos_men.count()} resultados")
    
    # Intento 3: Ver todos los estilos sin filtro de género
    all_cuadrado = HaircutStyleModel.objects.filter(
        suitable_for_shapes__contains=['cuadrado']
    )
    print(f"   Método 3 (sin filtro género): {all_cuadrado.count()} resultados")
    
    if all_cuadrado.exists():
        print(f"\n   📝 Estilos encontrados para 'cuadrado' (cualquier género):")
        for s in all_cuadrado[:3]:
            print(f"      - {s.name} (gender={s.gender})")
    
    print("="*80 + "\n")

def generate_style_recommendations(face_shape_str, gender_str, hair_length_str, user_id):
    """
    Genera recomendaciones de estilos basadas en el análisis facial
    """
    print(">>> ENTRANDO A generate_style_recommendations")
    print(f"    Parámetros recibidos: face_shape={face_shape_str}, gender={gender_str}, hair_length={hair_length_str}")
    
    # Inicializar variables para evitar UnboundLocalError
    confidence = 0.0
    tips = {}
    haircut_styles = []
    beard_styles = []

    try:
        # 🔧 MAPEO DE GÉNERO MEJORADO
        GENDER_MAPPING = {
            'male': Gender.HOMBRE,
            'hombre': Gender.HOMBRE,
            'men': Gender.HOMBRE,
            'masculino': Gender.HOMBRE,
            'female': Gender.MUJER,
            'mujer': Gender.MUJER,
            'women': Gender.MUJER,
            'femenino': Gender.MUJER,
            'prefer_not_to_say': Gender.HOMBRE,  # Default
            'otro': Gender.HOMBRE,  # Default
        }
        
        # Normalizar y mapear FaceShape
        face_shape_normalized = face_shape_str.lower().strip()
        face_shape = FACE_SHAPE_MAPPING.get(face_shape_normalized, FaceShape.OVAL)
        print(f"    ✓ Face shape mapeada: {face_shape}")
        
        # Mapear género usando el diccionario
        gender_normalized = gender_str.lower().strip()
        gender = GENDER_MAPPING.get(gender_normalized, Gender.HOMBRE)
        print(f"    ✓ Género mapeado: '{gender_str}' → {gender}")
        
        # Mapear longitud de cabello
        HAIR_LENGTH_MAPPING = {
            'corto': HairLength.CORTO,
            'short': HairLength.CORTO,
            'medio': HairLength.MEDIO,
            'medium': HairLength.MEDIO,
            'largo': HairLength.LARGO,
            'long': HairLength.LARGO,
        }
        hair_length = HAIR_LENGTH_MAPPING.get(hair_length_str.lower().strip(), HairLength.MEDIO)
        print(f"    ✓ Hair length mapeada: {hair_length}")

        # Generar recomendaciones de cortes
        print(f"    🔍 Llamando a GenerateHaircutRecommendationsUseCase...")
        haircut_use_case = GenerateHaircutRecommendationsUseCase(recommendation_engine, style_catalog)
        haircut_styles = haircut_use_case.execute(
            face_shape=face_shape, 
            gender=gender, 
            hair_length=hair_length, 
            max_results=6
        )
        print(f"    ✓ Cortes obtenidos: {len(haircut_styles)}")
        
        if not haircut_styles:
            print(f"    ⚠️ WARNING: No se encontraron estilos de corte para:")
            print(f"       - face_shape={face_shape}")
            print(f"       - gender={gender}")
            print(f"       - hair_length={hair_length}")

        # Generar recomendaciones de barba (solo hombres)
        if gender == Gender.HOMBRE:
            print(f"    🔍 Llamando a GenerateBeardRecommendationsUseCase...")
            beard_use_case = GenerateBeardRecommendationsUseCase(recommendation_engine, style_catalog)
            beard_styles = beard_use_case.execute(face_shape=face_shape, gender=gender, max_results=4)
            print(f"    ✓ Estilos de barba obtenidos: {len(beard_styles)}")

        # Calcular confidence si hay cortes
        if haircut_styles:
            confidence = sum(
                recommendation_engine.calculate_style_score(style, face_shape, gender, hair_length)
                for style in haircut_styles
            ) / len(haircut_styles) * 100
            print(f"    ✓ Confidence calculada: {confidence:.2f}%")

        # Obtener tips
        tips = recommendation_engine.get_face_shape_tips(face_shape)
        print(f"    ✓ Tips obtenidos: {len(tips) if tips else 0}")

        # Crear diccionario de recomendaciones
        recommendations = {
            'cortes': [
                {
                    'nombre': s.name,
                    'descripcion': s.description,
                    'imagen': s.image_url or f'https://via.placeholder.com/300x400?text={s.name.replace(" ", "+")}',
                    'beneficios': s.benefits
                } for s in haircut_styles
            ],
            'barba': [
                {
                    'nombre': s.name,
                    'descripcion': s.description,
                    'imagen': s.image_url or f'https://via.placeholder.com/300x400?text={s.name.replace(" ", "+")}'
                } for s in beard_styles
            ],
            'confidence': confidence,
            'tips': tips
        }

        print(f"    ✅ ÉXITO: Recomendaciones generadas:")
        print(f"       - {len(recommendations['cortes'])} cortes")
        print(f"       - {len(recommendations['barba'])} estilos de barba")
        if recommendations['cortes']:
            print(f"       - Primera recomendación: {recommendations['cortes'][0]['nombre']}")
        
        return recommendations

    except Exception as e:
        print(f"✗✗✗ ERROR en generate_style_recommendations: {e}")
        import traceback
        traceback.print_exc()
        return None



def results(request):
    """Vista de resultados del análisis facial con recomendaciones"""
    camera = VideoCamera()
    predictions_collected = False

    try:
        start_time = time.time()
        # Recoger predicciones durante 12 segundos
        while time.time() - start_time < 5:
            _ = camera.get_frame()
            if len(camera.predictions_history) >= 8:
                predictions_collected = True
                break
            time.sleep(0.05)

        # Obtener resultados agregados
        face_shape_results = camera.get_aggregated_predictions()

        if not predictions_collected:
            context = {
                'analysis': {
                    'face_shape_results': [("No se detectó rostro", 0)],
                    'primary_shape': "No se detectó rostro",
                    'primary_confidence': 0,
                    'gender': 'no_detectado',
                    'measurements': None
                },
                'error_message': "No se pudo detectar un rostro. Por favor, asegúrate de estar bien iluminado y mirando directamente a la cámara.",
                'recommendations': None
            }

        else:
            # Usar el último frame
            frame_array = getattr(camera, 'last_frame', None)
            face_data = None
            try:
                if frame_array is not None:
                    _, face_data = camera.face_detector.detect_face_shape(frame_array)
            except Exception:
                traceback.print_exc()
                face_data = None

            metrics = camera.calculate_facial_metrics(face_data[0]) if face_data else None
            primary_shape = face_shape_results[0][0] if face_shape_results else "No detectado"
            primary_confidence = face_shape_results[0][1] if face_shape_results else 0

            # 🧠 Obtener género del perfil
            user_profile = None
            user_gender = "prefer_not_to_say"

            if request.user.is_authenticated:
                try:
                    user_profile = ProfileModel.objects.get(user=request.user)
                    user_gender = user_profile.gender or "prefer_not_to_say"
                except ProfileModel.DoesNotExist:
                    print("⚠️ El usuario autenticado no tiene un perfil asociado.")

            # Generar recomendaciones automáticamente
            recommendations = None
            if primary_shape != "No detectado":
                print("=" * 80)
                print(f"🔍 INICIANDO GENERACIÓN DE RECOMENDACIONES")
                print(f"   Forma detectada: '{primary_shape}'")
                print(f"   Género del perfil: '{user_gender}'")
                print("=" * 80)

                
                debug_database_content()
                
                try:
                    recommendations = generate_style_recommendations(
                        face_shape_str=primary_shape,
                        gender_str=user_gender,
                        hair_length_str='medio',
                        user_id=str(request.user.id) if request.user.is_authenticated else str(uuid.uuid4())
                    )

                    if recommendations:
                        print(f"✓✓✓ ÉXITO: {len(recommendations['cortes'])} cortes generados")
                        print(f"    Primera recomendación: {recommendations['cortes'][0]['nombre']}")
                    else:
                        print("✗✗✗ ERROR: generate_style_recommendations retornó None")

                except Exception as e:
                    print(f"✗✗✗ EXCEPCIÓN al generar recomendaciones: {e}")
                    traceback.print_exc()
                    recommendations = None

                print("=" * 80)
            else:
                print("⚠️ No se generan recomendaciones: primary_shape = 'No detectado'")
            # 🆕🆕🆕 GUARDAR EN EL HISTORIAL AUTOMÁTICAMENTE 🆕🆕🆕
            if primary_shape != "No detectado" and recommendations and request.user.is_authenticated:
                try:
                    print("\n" + "🔷" * 40)
                    print("💾 GUARDANDO ANÁLISIS EN HISTORIAL...")
                    
                    # 🔧 Función helper para convertir tipos NumPy a Python nativos
                    def convert_to_native(obj):
                        """Convierte tipos NumPy a tipos Python nativos para JSON"""
                        if isinstance(obj, np.integer):
                            return int(obj)
                        elif isinstance(obj, np.floating):
                            return float(obj)
                        elif isinstance(obj, np.ndarray):
                            return obj.tolist()
                        elif isinstance(obj, dict):
                            return {key: convert_to_native(value) for key, value in obj.items()}
                        elif isinstance(obj, list):
                            return [convert_to_native(item) for item in obj]
                        else:
                            return obj
                    
                    # Preparar datos del análisis (convertir NumPy types)
                    analysis_data_dict = {
                        'primary_shape': str(primary_shape),
                        'primary_confidence': float(primary_confidence),
                        'face_shape_results': [
                            [str(shape), float(percent)] 
                            for shape, percent in face_shape_results
                        ],
                        'measurements': convert_to_native(metrics) if metrics else {},
                        'gender': str(user_gender)  # 🔧 Agregar género
                    }
                    
                    # Preparar datos de recomendaciones
                    recommendations_data_dict = {
                        'cortes': [
                            {
                                'nombre': str(c.get('nombre', '')),
                                'descripcion': str(c.get('descripcion', '')),
                                'beneficios': [str(b) for b in c.get('beneficios', [])],
                                'caracteristicas': [str(b) for b in c.get('beneficios', [])]
                            }
                            for c in recommendations.get('cortes', [])
                        ],
                        'barbas': [
                            {
                                'nombre': str(b.get('nombre', '')),
                                'descripcion': str(b.get('descripcion', '')),
                                'caracteristicas': []
                            }
                            for b in recommendations.get('barba', [])
                        ] if recommendations.get('barba') else [],
                        'tips': convert_to_native(recommendations.get('tips', {}))
                    }
                    
                    # 🆕 GUARDAR LA IMAGEN DEL ROSTRO
                    image_path_value = None
                    if frame_array is not None:
                        try:
                            # Convertir frame a JPEG
                            _, buffer = cv2.imencode('.jpg', frame_array)
                            image_file = ContentFile(buffer.tobytes())
                            
                            # Generar nombre único
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            filename = f'analysis_{request.user.id}_{timestamp}.jpg'
                            
                            # Guardar usando el storage de Django
                            from django.core.files.storage import default_storage
                            saved_path = default_storage.save(
                                f'analysis_images/{datetime.now().strftime("%Y/%m/%d")}/{filename}',
                                image_file
                            )
                            image_path_value = saved_path
                            
                            print(f"📸 Imagen guardada en: {saved_path}")
                        except Exception as img_error:
                            print(f"⚠️ Error al guardar imagen: {img_error}")
                            import traceback as tb
                            tb.print_exc()
                    
                    # 🆕 CREAR LA ENTIDAD AnalysisHistory
                    analysis_history_entity = AnalysisHistory(
                        id=None,  # Se generará en la BD
                        user_id=str(request.user.id),
                        face_shape=str(primary_shape),
                        confidence=float(primary_confidence),
                        analysis_data=json.dumps(analysis_data_dict),
                        recommendations_data=json.dumps(recommendations_data_dict),
                        recommendations_count=len(recommendations.get('cortes', [])) + len(recommendations.get('barba', []) or []),
                        pdf_path=None,
                        image_path=image_path_value,  # 🆕 AGREGAR IMAGEN
                        created_at=datetime.now()  # 🔧 Usar datetime.now() en lugar de timezone.now() para compatibilidad
                    )
                    
                    # 🆕 GUARDAR LA ENTIDAD
                    history_entry = history_repository.save(analysis_history_entity)
                    
                    print(f"✅ Análisis guardado en historial con ID: {history_entry.id}")
                    print(f"   Usuario: {request.user.username}")
                    print(f"   Forma: {primary_shape}")
                    print(f"   Imagen: {image_path_value or 'Sin imagen'}")
                    print(f"   Recomendaciones: {len(recommendations.get('cortes', []))} cortes")
                    print("🔷" * 40 + "\n")
                    
                    context_history_id = history_entry.id
                    
                except Exception as e:
                    print(f"❌ ERROR al guardar en historial: {e}")
                    import traceback as tb
                    tb.print_exc()
                    context_history_id = None
            else:
                context_history_id = None
                if not request.user.is_authenticated:
                    print("⚠️ Usuario no autenticado, no se guarda en historial")
                else:
                    print("⚠️ No se guarda: primary_shape no detectado o sin recomendaciones")
                    
            context = {
                'analysis': {
                    'face_shape_results': face_shape_results,
                    'primary_shape': primary_shape,
                    'primary_confidence': primary_confidence,
                    'gender': user_gender,
                    'measurements': metrics
                },
                'recommendations': recommendations,
                'history_id': context_history_id  # 🆕 ID del análisis guardado

            }
            # Serializar datos para JavaScript
            analysis = context['analysis']
            
            context['analysis_json'] = json.dumps({
                'primary_shape': analysis.get('primary_shape', ''),
                'primary_confidence': float(analysis.get('primary_confidence', 0)),
                'face_shape_results': [
                    [str(shape), float(percent)] 
                    for shape, percent in analysis.get('face_shape_results', [])
                ],
                'measurements': {
                    k: float(v) if isinstance(v, (int, float)) else str(v)
                    for k, v in (analysis.get('measurements') or {}).items()
                } if analysis.get('measurements') else {}
            })
    
            context['recommendations_json'] = json.dumps({
                'cortes': [
                    {
                        'nombre': c.get('nombre', ''),
                        'descripcion': c.get('descripcion', ''),
                        'beneficios': c.get('beneficios', [])
                    }
                    for c in recommendations.get('cortes', [])[:3]
                ] if recommendations else [],
                'barba': [
                    {
                        'nombre': b.get('nombre', ''),
                        'descripcion': b.get('descripcion', '')
                    }
                    for b in recommendations.get('barba', [])
                ] if recommendations else [],
                'tips': recommendations.get('tips', {}) if recommendations else {}
            })
        return render(request, 'analysis/results.html', context)

    finally:
        if hasattr(camera, 'video') and camera.video.isOpened():
            camera.video.release()
            
def main(request):
    """Vista principal del análisis"""
    global stop_camera
    stop_camera = False  # 🔄 Reiniciar bandera cuando se carga la página principal
    return render(request, 'analysis/analysis.html')


class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.face_detector = FaceShapeDetector()
        self.predictions_history = []
        self.last_frame = None
        try:
            self.classifier = FaceShapeClassifier()
            # Reparar compatibilidad de estimadores sklearn
            try:
                model = getattr(self.classifier, 'model', None)
                if model is not None:
                    estimators = getattr(model, 'estimators_', None)
                    if estimators:
                        for est in estimators:
                            if not hasattr(est, 'monotonic_cst'):
                                setattr(est, 'monotonic_cst', None)
            except Exception:
                traceback.print_exc()
        except Exception as e:
            print(f"Error initializing classifier: {e}")
            self.classifier = None

    def __del__(self):
        if hasattr(self, 'video') and self.video.isOpened():
            self.video.release()

    def get_aggregated_predictions(self):
        if not self.predictions_history:
            return [("No detectado", 0)]
        face_types = {}
        total_confidence = {}
        total_predictions = len(self.predictions_history)
        for pred, conf in self.predictions_history:
            face_types.setdefault(pred, 0)
            total_confidence.setdefault(pred, 0)
            face_types[pred] += 1
            total_confidence[pred] += conf
        results = []
        for face_type, count in face_types.items():
            percentage = (count / total_predictions) * 100
            avg_confidence = total_confidence[face_type] / count
            results.append((face_type, percentage, avg_confidence))
        results.sort(key=lambda x: x[1], reverse=True)
        return [(face_type, percentage) for face_type, percentage, _ in results]

    def get_frame(self):
        global stop_camera
        if stop_camera:
            print("📷 get_frame detenido: stop_camera=True")
            if hasattr(self, 'video') and self.video.isOpened():
                self.video.release()
            return None
        success, image = self.video.read()
        if not success:
            return None
        self.last_frame = image.copy()
        try:
            processed_image, face_data = self.face_detector.detect_face_shape(image.copy())
            if face_data and self.classifier:
                face_info = face_data[0]
                face_region = image[
                    face_info['bbox'][1]:face_info['bbox'][1] + face_info['bbox'][3],
                    face_info['bbox'][0]:face_info['bbox'][0] + face_info['bbox'][2]
                ]
                try:
                    features = self.classifier.extract_features(face_region, face_info['measurements'])
                    features = np.array(features).reshape(1, -1)
                    try:
                        prediction, confidence = self.classifier.predict(features)
                    except AttributeError:
                        model = getattr(self.classifier, 'model', None)
                        if model is not None:
                            estimators = getattr(model, 'estimators_', None)
                            if estimators:
                                for est in estimators:
                                    if not hasattr(est, 'monotonic_cst'):
                                        setattr(est, 'monotonic_cst', None)
                        prediction, confidence = self.classifier.predict(features)

                    self.predictions_history.append((prediction, confidence))
                    if len(self.predictions_history) > 60:
                        self.predictions_history.pop(0)
                    x, y, w, h = face_info['bbox']
                    cv2.putText(processed_image,
                               f"Forma: {prediction} ({confidence:.2f})",
                               (x, y - 10),
                               cv2.FONT_HERSHEY_SIMPLEX,
                               0.7,
                               (0, 255, 0),
                               2)
                except Exception:
                    traceback.print_exc()
            _, jpeg = cv2.imencode('.jpg', processed_image)
            return jpeg.tobytes()
        except Exception:
            traceback.print_exc()
            return None

    def calculate_facial_metrics(self, face_info):
        measurements = face_info.get('measurements', {}) if face_info else {}
        
        eye_distance_px = measurements.get('eye_distance', 0)
        if eye_distance_px > 0:
            px_to_cm = 6.3 / eye_distance_px
        else:
            px_to_cm = 0

        height = measurements.get('height', 0) * px_to_cm
        width = measurements.get('width', 0) * px_to_cm
        
        upper_third = height * 0.3333
        middle_third = height * 0.3333
        lower_third = height * 0.3333
        
        symmetry = 0
        if width:
            forehead = measurements.get('forehead_width', 0) * px_to_cm
            jaw = measurements.get('jaw_width', 0) * px_to_cm
            symmetry = 100 - (abs(forehead - jaw) / width * 100)

        return {
            'face_height': round(height, 1),
            'face_width': round(width, 1),
            'upper_third': round(upper_third, 1),
            'middle_third': round(middle_third, 1),
            'lower_third': round(lower_third, 1),
            'eye_distance': round(eye_distance_px * px_to_cm, 1),
            'forehead_width': round(measurements.get('forehead_width', 0) * px_to_cm, 1),
            'jaw_width': round(measurements.get('jaw_width', 0) * px_to_cm, 1),
            'nose_length': round(measurements.get('nose_length', 0) * px_to_cm, 1),
            'ratio': round(measurements.get('ratio', 0), 2),
            'symmetry': round(symmetry, 1)
        }


def gen(camera):
    global stop_camera
    try:
        while True:
            if stop_camera:
                print("📷 Stream detenido por stop_camera")
                break
            frame = camera.get_frame()
            if frame is None:
                print("⚠️ No se pudo capturar frame (cámara desconectada o detenida)")
                break
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    finally:
        if hasattr(camera, 'video') and camera.video.isOpened():
            camera.video.release()
        print("📷 Cámara liberada correctamente")
        
def stop_video(request):
    global stop_camera
    stop_camera = True
    print("📷 Señal recibida: detener cámara")
    return JsonResponse({'status': 'ok', 'message': 'Camera stopped'})


@gzip.gzip_page
def video_feed(request):
    try:
        return StreamingHttpResponse(
            gen(VideoCamera()),
            content_type='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        print(f"Error in video feed: {str(e)}")
        return HttpResponse("Video feed error")