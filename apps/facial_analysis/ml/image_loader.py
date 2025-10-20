# apps/facial_analysis/ml/image_loader.py
import os
from pathlib import Path
from PIL import Image
import cv2
import numpy as np

from apps.facial_analysis.ml.face_shape_classifier import FaceShapeClassifier

class ImageLoader:
    """
    Carga imágenes desde carpetas organizadas por etiquetas
    Estructura esperada:
    
    dataset/
    ├── Redonda/
    │   ├── img1.jpg
    │   ├── img2.jpg
    │   └── ...
    ├── Ovalada/
    │   ├── img1.jpg
    │   └── ...
    └── ...
    """
    
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.classes = ['Redonda', 'Ovalada', 'Diamante', 'Cuadrada', 'Corazón', 'Triangular']
        self.valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    
    def load_images_from_directory(self, face_detector=None):
        """
        Carga todas las imágenes del dataset
        
        Args:
            face_detector: instancia de FaceShapeDetector para extraer rostros
        
        Returns:
            (features_list, labels_list, images_loaded_count)
        """
        features_list = []
        labels_list = []
        loaded_count = 0
        failed_count = 0
        
        for class_name in self.classes:
            class_path = os.path.join(self.dataset_path, class_name)
            
            if not os.path.exists(class_path):
                print(f"⚠ Carpeta no encontrada: {class_path}")
                continue
            
            print(f"\n[*] Cargando imágenes de: {class_name}")
            
            image_files = [f for f in os.listdir(class_path) 
                          if Path(f).suffix.lower() in self.valid_extensions]
            
            print(f"    Imágenes encontradas: {len(image_files)}")
            
            for idx, image_file in enumerate(image_files):
                try:
                    image_path = os.path.join(class_path, image_file)
                    
                    # Cargar imagen
                    image = cv2.imread(image_path)
                    if image is None:
                        raise ValueError("No se pudo leer la imagen")
                    
                    # Detectar rostro y extraer características
                    if face_detector is not None:
                        _, face_data = face_detector.detect_face_shape(image.copy())
                        
                        if not face_data:
                            print(f"    ⚠ [{idx+1}/{len(image_files)}] {image_file}: No se detectó rostro")
                            failed_count += 1
                            continue
                        
                        # Usar el primer rostro detectado
                        face_info = face_data[0]
                        face_region = image[
                            face_info['bbox'][1]:face_info['bbox'][1] + face_info['bbox'][3],
                            face_info['bbox'][0]:face_info['bbox'][0] + face_info['bbox'][2]
                        ]
                        
                        # Extraer features
                        from apps.facial_analysis.ml.face_shape_classifier import FaceShapeClassifier
                        classifier = FaceShapeClassifier()
                        features = classifier.extract_features(face_region, face_info['measurements'])
                    else:
                        raise ValueError("Face detector requerido")
                    
                    features_list.append(features)
                    labels_list.append(class_name)
                    loaded_count += 1
                    
                    if (idx + 1) % 5 == 0:
                        print(f"    ✓ [{idx+1}/{len(image_files)}] Procesadas")
                
                except Exception as e:
                    print(f"    ✗ [{idx+1}/{len(image_files)}] {image_file}: {str(e)}")
                    failed_count += 1
        
        print(f"\n✓ Carga completa!")
        print(f"  - Imágenes procesadas: {loaded_count}")
        print(f"  - Errores: {failed_count}")
        
        return np.array(features_list), np.array(labels_list), loaded_count
    
    def load_single_image(self, image_path, face_detector):
        """
        Carga una imagen individual
        
        Args:
            image_path: ruta a la imagen
            face_detector: detector de rostros
        
        Returns:
            (features, face_image) o None si falla
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("No se pudo leer la imagen")
            
            _, face_data = face_detector.detect_face_shape(image.copy())
            
            if not face_data:
                print(f"⚠ No se detectó rostro en {image_path}")
                return None
            
            face_info = face_data[0]
            face_region = image[
                face_info['bbox'][1]:face_info['bbox'][1] + face_info['bbox'][3],
                face_info['bbox'][0]:face_info['bbox'][0] + face_info['bbox'][2]
            ]
            
            classifier = FaceShapeClassifier()
            features = classifier.extract_features(face_region, face_info['measurements'])
            
            return features, face_region
        
        except Exception as e:
            print(f"✗ Error al cargar {image_path}: {e}")
            return None
    
    def validate_dataset_structure(self):
        """
        Valida la estructura del dataset
        """
        print("[*] Validando estructura del dataset...")
        
        for class_name in self.classes:
            class_path = os.path.join(self.dataset_path, class_name)
            
            if not os.path.exists(class_path):
                print(f"  ✗ Carpeta faltante: {class_name}")
                return False
            
            images = [f for f in os.listdir(class_path) 
                     if Path(f).suffix.lower() in self.valid_extensions]
            
            if len(images) == 0:
                print(f"  ⚠ Carpeta vacía: {class_name}")
            else:
                print(f"  ✓ {class_name}: {len(images)} imágenes")
        
        return True