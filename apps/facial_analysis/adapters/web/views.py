import time
import traceback
from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponse
from django.views.decorators import gzip
from apps.facial_analysis.face_shape_detection import FaceShapeDetector
from apps.facial_analysis.ml.face_shape_classifier import FaceShapeClassifier
import cv2
import numpy as np
# Create your views here.
def main(request):
  return render(request, 'analysis/analysis.html')
def results(request):
    camera = VideoCamera()
    predictions_collected = False

    try:
        start_time = time.time()
        # aumentar tiempo total y reducir frecuencia para no saturar CPU
        while time.time() - start_time < 12:  # 12s para asegurar warmup + varias predicciones
            _ = camera.get_frame()  # get_frame actualiza camera.last_frame internamente
            # verificar historial de predicciones
            if len(camera.predictions_history) >= 8:  # recoger al menos 8 predicciones
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
                'error_message': "No se pudo detectar un rostro. Por favor, asegúrate de estar bien iluminado y mirando directamente a la cámara."
            }
        else:
            # Usar el último frame en formato array (no los bytes JPEG)
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

            context = {
                'analysis': {
                    'face_shape_results': face_shape_results,
                    'primary_shape': primary_shape,
                    'primary_confidence': primary_confidence,
                    'gender': 'hombre',
                    'measurements': metrics
                }
            }

        return render(request, 'analysis/results.html', context)

    finally:
        if hasattr(camera, 'video') and camera.video.isOpened():
            camera.video.release()




class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.face_detector = FaceShapeDetector()
        self.predictions_history = []
        self.last_frame = None
        try:
            self.classifier = FaceShapeClassifier()
            # Si el modelo ya está cargado, reparar compatibilidad de estimadores sklearn
            try:
                model = getattr(self.classifier, 'model', None)
                if model is not None:
                    estimators = getattr(model, 'estimators_', None)
                    if estimators:
                        for est in estimators:
                            # versiones antiguas pueden no tener este atributo -> establecer None
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
        success, image = self.video.read()
        if not success:
            return None
        # guardar último frame array para uso posterior en results
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
                    # re-parchar estimadores si falla la primera vez (segundo intento)
                    try:
                        prediction, confidence = self.classifier.predict(features)
                    except AttributeError as ae:
                        # intentar reparar estimadores y reintentar
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
        
        # Factor de conversión basado en la distancia entre ojos (6.3 cm promedio)
        eye_distance_px = measurements.get('eye_distance', 0)
        if eye_distance_px > 0:
            # Calculamos cuántos píxeles equivalen a 1 cm
            px_to_cm = 6.3 / eye_distance_px
        else:
            px_to_cm = 0

        # Convertir medidas de píxeles a centímetros
        height = measurements.get('height', 0) * px_to_cm
        width = measurements.get('width', 0) * px_to_cm
        
        # Calcular tercios verticales
        upper_third = height * 0.3333
        middle_third = height * 0.3333
        lower_third = height * 0.3333
        
        # Calcular simetría
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
            'ratio': round(measurements.get('ratio', 0), 2),  # Este es un ratio, no necesita conversión
            'symmetry': round(symmetry, 1)  # Porcentaje, no necesita conversión
        }


def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

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