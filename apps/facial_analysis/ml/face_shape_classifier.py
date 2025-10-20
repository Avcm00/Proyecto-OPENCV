# apps/facial_analysis/ml/face_shape_classifier.py
import numpy as np
import pickle
import os
import cv2
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

class FaceShapeClassifier:
    """
    Modelo de ML para clasificar formas de rostro usando Random Forest
    Clasifica en 5 categorías: Corazón, Diamante, Ovalado, Redondo, Triangular
    """
    
    def __init__(self, model_path=None):
        self.model = None
        self.scaler = StandardScaler()
        # 5 clases actualizadas
        self.classes = ['Corazón', 'Diamante', 'Ovalado', 'Redondo', 'Triangular']
        self.model_path = model_path or 'apps/facial_analysis/ml/models/face_shape_model.pkl'
        self.scaler_path = model_path or 'apps/facial_analysis/ml/models/scaler.pkl'
        
        # Crear directorio de modelos si no existe
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        # Cargar modelo si existe
        if os.path.exists(self.model_path):
            self.load_model()
    
    def extract_features(self, face_region, measurements):
        """
        Extrae características del rostro para el modelo
        
        Args:
            face_region: región de la cara (imagen OpenCV)
            measurements: diccionario con medidas calculadas
        
        Returns:
            array de características (11 features)
        """
        features = []
        
        # 1. Ratios básicos
        features.append(measurements['ratio'])  # altura/ancho
        features.append(measurements['forehead_to_middle_ratio'])
        features.append(measurements['jaw_to_middle_ratio'])
        features.append(measurements['forehead_to_jaw_ratio'])
        
        # 2. Proporciones de ancho
        face_width = measurements['width']
        forehead_ratio = measurements['forehead_width'] / max(face_width, 1)
        middle_ratio = measurements['middle_width'] / max(face_width, 1)
        jaw_ratio = measurements['jaw_width'] / max(face_width, 1)
        
        features.append(forehead_ratio)
        features.append(middle_ratio)
        features.append(jaw_ratio)
        
        # 3. Variabilidad de anchos (para detectar diamante)
        widths = [measurements['forehead_width'], 
                  measurements['middle_width'], 
                  measurements['jaw_width']]
        width_std = np.std(widths) / max(np.mean(widths), 1)
        width_max_diff = (max(widths) - min(widths)) / max(np.mean(widths), 1)
        
        features.append(width_std)
        features.append(width_max_diff)
        
        # 4. Características de la imagen
        gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        
        # Contraste
        contrast = np.std(gray) / 255.0
        features.append(contrast)
        
        # Suavidad
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        smoothness = np.sum(np.abs(gray.astype(float) - blurred.astype(float))) / (gray.size * 255)
        features.append(smoothness)
        
        return np.array(features)
    
    def train(self, X, y, test_size=0.2):
        """
        Entrena el modelo Random Forest
        
        Args:
            X: features array (N, 11)
            y: labels array (N,)
            test_size: porcentaje para test
        
        Returns:
            dict con métricas de entrenamiento
        """
        print(f"[*] Normalizando características...")
        X_scaled = self.scaler.fit_transform(X)
        
        print(f"[*] Dividiendo datos: train {100-test_size*100:.0f}%, test {test_size*100:.0f}%")
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=test_size, random_state=42, stratify=y
        )
        
        print(f"[*] Creando modelo Random Forest...")
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
            verbose=1
        )
        
        print(f"[*] Entrenando modelo...")
        self.model.fit(X_train, y_train)
        
        # Evaluar
        train_accuracy = self.model.score(X_train, y_train)
        test_accuracy = self.model.score(X_test, y_test)
        
        y_pred = self.model.predict(X_test)
        
        print(f"\n✓ Entrenamiento completado!")
        print(f"  - Precisión entrenamiento: {train_accuracy:.4f}")
        print(f"  - Precisión test: {test_accuracy:.4f}")
        print(f"\nReporte de clasificación:")
        print(classification_report(y_test, y_pred, target_names=self.classes))
        
        return {
            'train_accuracy': train_accuracy,
            'test_accuracy': test_accuracy,
            'y_true': y_test,
            'y_pred': y_pred,
            'classes': self.classes
        }
    
    def predict(self, features):
        """
        Predice la forma del rostro
        
        Args:
            features: array de características
        
        Returns:
            (clase_predicha, confianza)
        """
        if self.model is None:
            raise ValueError("Modelo no entrenado")
        
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]
        confidence = np.max(probabilities)
        
        return prediction, confidence
    
    def predict_batch(self, features_list):
        """
        Predice múltiples rostros
        
        Args:
            features_list: lista de arrays de características
        
        Returns:
            lista de (predicción, confianza)
        """
        if self.model is None:
            raise ValueError("Modelo no entrenado")
        
        features_scaled = self.scaler.transform(features_list)
        predictions = self.model.predict(features_scaled)
        probabilities = self.model.predict_proba(features_scaled)
        confidences = np.max(probabilities, axis=1)
        
        return list(zip(predictions, confidences))
    
    def save_model(self):
        """Guarda el modelo y el scaler"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        with open(self.scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        print(f"✓ Modelo guardado: {self.model_path}")
    
    def load_model(self):
        """Carga el modelo y el scaler"""
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            with open(self.scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            
            print(f"✓ Modelo cargado: {self.model_path}")
        except Exception as e:
            print(f"✗ Error al cargar modelo: {e}")
            self.model = None


# apps/facial_analysis/ml/image_loader.py
import os
from pathlib import Path
from PIL import Image
import cv2
import numpy as np

class ImageLoader:
    """
    Carga imágenes desde carpetas organizadas por etiquetas
    Estructura esperada: dataset/faces/{Corazón, Diamante, Ovalado, Redondo, Triangular}/
    """
    
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        # 5 clases actualizadas
        self.classes = ['Corazón', 'Diamante', 'Ovalado', 'Redondo', 'Triangular']
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
        """Carga una imagen individual"""
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
            
            from apps.facial_analysis.ml.face_shape_classifier import FaceShapeClassifier
            classifier = FaceShapeClassifier()
            features = classifier.extract_features(face_region, face_info['measurements'])
            
            return features, face_region
        
        except Exception as e:
            print(f"✗ Error al cargar {image_path}: {e}")
            return None
    
    def validate_dataset_structure(self):
        """Valida la estructura del dataset"""
        print("[*] Validando estructura del dataset...")
        
        all_exist = True
        for class_name in self.classes:
            class_path = os.path.join(self.dataset_path, class_name)
            
            if not os.path.exists(class_path):
                print(f"  ✗ Carpeta faltante: {class_name}")
                all_exist = False
            else:
                images = [f for f in os.listdir(class_path) 
                         if Path(f).suffix.lower() in self.valid_extensions]
                
                if len(images) == 0:
                    print(f"  ⚠ Carpeta vacía: {class_name}")
                else:
                    print(f"  ✓ {class_name}: {len(images)} imágenes")
        
        return all_exist