import time
import traceback
from celery import uuid
from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse, HttpResponse
from django.views.decorators import gzip
from apps.auth_app.adapters.persistence.models import ProfileModel
from apps.facial_analysis.face_shape_detection import FaceShapeDetector
from apps.facial_analysis.ml.face_shape_classifier import FaceShapeClassifier
import cv2
import numpy as np

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

# Inicializar dependencias de recomendaciones (una vez)
style_repository = DjangoStyleRepository()
recommendation_repository = DjangoRecommendationRepository()
recommendation_engine = RuleBasedRecommendationEngine()
style_catalog = StyleCatalogServiceImpl(style_repository)
stop_camera = False  # Bandera global para detener la cámara
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


def generate_style_recommendations(face_shape_str, gender_str, hair_length_str, user_id):
    """
    Genera recomendaciones de estilos basadas en el análisis facial
    
    Args:
        face_shape_str: Forma del rostro detectada (str)
        gender_str: Género del usuario (str)
        hair_length_str: Longitud del cabello (str)
        user_id: ID del usuario
    
    Returns:
        dict con recomendaciones de cortes y barbas
    """
    print("\n" + ">" * 80)
    print(f">>> ENTRANDO A generate_style_recommendations")
    print(f"    face_shape_str = '{face_shape_str}'")
    print(f"    gender_str = '{gender_str}'")
    print(f"    hair_length_str = '{hair_length_str}'")
    print(f"    user_id = {user_id}")
    
    try:
        # Normalizar y convertir strings a enums
        face_shape_normalized = face_shape_str.lower().strip()
        print(f"    Normalizado: '{face_shape_normalized}'")
        
        # Buscar en el mapeo
        face_shape = FACE_SHAPE_MAPPING.get(face_shape_normalized)
        print(f"    En mapeo: {face_shape}")
        
        if not face_shape:
            # Si no se encuentra, intentar directamente
            print(f"    ⚠️ No está en mapeo, intentando conversión directa...")
            try:
                face_shape = FaceShape(face_shape_normalized)
                print(f"    ✓ Conversión directa exitosa: {face_shape}")
            except ValueError as ve:
                print(f"    ✗ ValueError en conversión: {ve}")
                print(f"    Usando OVAL como fallback")
                face_shape = FaceShape.OVAL
        
        # Convertir género
        try:
            gender = Gender(gender_str.lower())
        except ValueError:
            gender = Gender.HOMBRE
        
        # Convertir longitud de cabello
        try:
            hair_length = HairLength(hair_length_str.lower())
            
        except ValueError:
            hair_length = HairLength.MEDIO
        
        print(f"Generando recomendaciones para: {face_shape.value}, {gender.value}, {hair_length.value}")
        
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
        
        print(f"Estilos de corte encontrados: {len(haircut_styles)}")
        
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
            print(f"Estilos de barba encontrados: {len(beard_styles)}")
        
        # Calcular confidence score
        confidence = 0.0
        if haircut_styles:
            confidence = sum(
                recommendation_engine.calculate_style_score(
                    style, face_shape, gender, hair_length
                )
                for style in haircut_styles
            ) / len(haircut_styles)
            confidence *= 100  # Convertir a porcentaje
        
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
        
        # Formatear para el template
        recommendations = {
            'id': saved_recommendation.id,
            'cortes': [
                {
                    'id': style.id,
                    'nombre': style.name,
                    'descripcion': style.description,
                    'imagen': style.image_url if style.image_url else 'https://via.placeholder.com/300x400?text=' + style.name.replace(' ', '+'),
                    'beneficios': style.benefits,
                    'dificultad': style.difficulty_level.value if hasattr(style.difficulty_level, 'value') else str(style.difficulty_level),
                    'popularidad': style.popularity_score
                }
                for style in haircut_styles
            ],
            'barba': [
                {
                    'id': style.id,
                    'nombre': style.name,
                    'descripcion': style.description,
                    'imagen': style.image_url if style.image_url else 'https://via.placeholder.com/300x400?text=' + style.name.replace(' ', '+'),
                    'beneficios': style.benefits,
                    'mantenimiento': style.maintenance_level.value if hasattr(style.maintenance_level, 'value') else str(style.maintenance_level)
                }
                for style in beard_styles
            ] if beard_styles else None,
            'confidence': confidence,
            'tips': tips
        }
        
        print(f"    ✓✓✓ Recomendaciones generadas exitosamente: {len(recommendations['cortes'])} cortes")
        print("<" * 80 + "\n")
        return recommendations
        print("DEBUG >>> haircut_styles =", haircut_styles)
        print("DEBUG >>> beard_styles =", beard_styles)

    except Exception as e:
        print(f"    ✗✗✗ ERROR CRÍTICO en generate_style_recommendations: {e}")
        print(f"    Tipo de error: {type(e).__name__}")
        traceback.print_exc()
        print("<" * 80 + "\n")
        return None



def results(request):
    """Vista de resultados del análisis facial con recomendaciones"""
    camera = VideoCamera()
    predictions_collected = False

    try:
        start_time = time.time()
        # Recoger predicciones durante 12 segundos
        while time.time() - start_time < 12:
            _ = camera.get_frame()
            if len(camera.predictions_history) >= 8:
                predictions_collected = True
                break
            time.sleep(0.15)

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

            context = {
                'analysis': {
                    'face_shape_results': face_shape_results,
                    'primary_shape': primary_shape,
                    'primary_confidence': primary_confidence,
                    'gender': user_gender,
                    'measurements': metrics
                },
                'recommendations': recommendations
            }

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