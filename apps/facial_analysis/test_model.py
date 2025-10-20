import cv2
import numpy as np
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apps.facial_analysis.face_shape_detection import FaceShapeDetector
from apps.facial_analysis.ml.face_shape_classifier import FaceShapeClassifier

def test_model(image_path):
    """
    Prueba el modelo con una imagen individual.
    
    Args:
        image_path: Ruta a la imagen a probar (ej: 'path/to/image.jpg')
    """
    print(f"\n[*] Probando modelo con imagen: {image_path}")
    
    # 1. Cargar la imagen
    image = cv2.imread(image_path)
    if image is None:
        print("✗ Error: No se pudo cargar la imagen.")
        return
    
    # 2. Inicializar detector y clasificador
    detector = FaceShapeDetector()
    classifier = FaceShapeClassifier()  # Esto carga el modelo automáticamente si existe
    
    # Verificar si el modelo está cargado
    if classifier.model is None:
        print("✗ Error: Modelo no encontrado. Entrénalo primero con 'python manage.py train_model' o 'python scripts/train_quick.py'.")
        return
    
    # 3. Detectar rostro y obtener datos
    processed_image, face_data = detector.detect_face_shape(image.copy())
    
    if not face_data:
        print("✗ No se detectó ningún rostro en la imagen.")
        return
    
    # Usar el primer rostro detectado
    face_info = face_data[0]
    face_region = image[
        face_info['bbox'][1]:face_info['bbox'][1] + face_info['bbox'][3],
        face_info['bbox'][0]:face_info['bbox'][0] + face_info['bbox'][2]
    ]
    
    # 4. Extraer características
    features = classifier.extract_features(face_region, face_info['measurements'])
    
    # 5. Hacer predicción
    prediction, confidence = classifier.predict(features)
    
    print("✓ Predicción completada!")
    print(f"  - Forma del rostro: {prediction}")
    print(f"  - Confianza: {confidence:.2f} ({confidence*100:.1f}%)")
    print(f"  - Mediciones: Ratio H/W = {face_info['measurements']['ratio']:.2f}")
    
    # 6. Mostrar imagen procesada (opcional)
    cv2.imshow('Resultado', processed_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python test_model.py <ruta_a_imagen>")
        print("Ejemplo: python test_model.py dataset/faces/Ovalado/ejemplo.jpg")
    else:
        test_model(sys.argv[1])
