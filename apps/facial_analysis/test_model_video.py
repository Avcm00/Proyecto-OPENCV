import cv2
import numpy as np
import sys
import os


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from apps.facial_analysis.face_shape_detection import FaceShapeDetector
    from apps.facial_analysis.ml.face_shape_classifier import FaceShapeClassifier
except ImportError as e:
    print(f"Error al importar módulos: {e}")
    print("Asegúrate de que:")
    print("  - El directorio 'apps' tenga un archivo '__init__.py'")
    print("  - Estés ejecutando el script desde el directorio correcto")
    sys.exit(1)

def test_model_on_video(video_source=0):
    """
    Prueba el modelo en tiempo real con video.
    
    Args:
        video_source: 0 para webcam, o ruta a archivo de video (ej: 'video.mp4')
    """
    print(f"\n[*] Probando modelo en video: {video_source}")
    
    # 1. Inicializar captura de video
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        print("✗ Error: No se pudo abrir la fuente de video.")
        return
    
    # 2. Inicializar detector y clasificador
    detector = FaceShapeDetector()
    classifier = FaceShapeClassifier()  # Carga el modelo automáticamente
    
    if classifier.model is None:
        print("✗ Error: Modelo no encontrado. Entrénalo primero con 'python manage.py train_model' o 'python scripts/train_quick.py'.")
        return
    
    print("✓ Modelo cargado. Presiona 'q' para salir.")
    
    while True:
        # Leer frame
        ret, frame = cap.read()
        if not ret:
            print("Fin del video o error al leer frame.")
            break
        
        # Procesar frame
        processed_frame, face_data = detector.detect_face_shape(frame.copy())
        
        if face_data:
            for face_info in face_data:
                # Extraer región del rostro
                face_region = frame[
                    face_info['bbox'][1]:face_info['bbox'][1] + face_info['bbox'][3],
                    face_info['bbox'][0]:face_info['bbox'][0] + face_info['bbox'][2]
                ]
                
                # Extraer características
                features = classifier.extract_features(face_region, face_info['measurements'])
                
                # Predecir
                prediction, confidence = classifier.predict(features)
                
                # Mostrar predicción en el frame
                x, y, w, h = face_info['bbox']
                cv2.putText(processed_frame, f'{prediction} ({confidence:.2f})', (x, y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Mostrar frame procesado
        cv2.imshow('Face Shape Detection', processed_frame)
        
        # Salir con 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()
    print("✓ Prueba finalizada.")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        # Usar webcam por defecto
        test_model_on_video(0)
    elif len(sys.argv) == 2:
        # Usar archivo de video
        test_model_on_video(sys.argv[1])
    else:
        print("Uso: python test_model_video.py [ruta_a_video]")
        print("Ejemplos:")
        print("  - Webcam: python test_model_video.py")
        print("  - Archivo: python test_model_video.py video.mp4")