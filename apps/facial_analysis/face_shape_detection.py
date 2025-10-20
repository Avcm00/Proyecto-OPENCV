# apps/facial_analysis/face_shape_detection.py
import cv2
import numpy as np

class FaceShapeDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    
    def analyze_face_contour(self, face_region):
        """Analiza el contorno de la cara"""
        gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray_face, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None, None
        
        largest_contour = max(contours, key=cv2.contourArea)
        return largest_contour, edges
    
    def calculate_face_measurements(self, x, y, w, h, face_region):
        """Calcula medidas faciales detalladas"""
        gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        
        face_width = w
        face_height = h
        face_ratio = face_height / face_width
        
        def get_width_by_projection(region, percentile=85):
            if region.size == 0:
                return region.shape[1] if len(region.shape) > 1 else 0
            
            projection = np.sum(region, axis=0)
            threshold = np.percentile(projection, percentile)
            valid_cols = np.where(projection > threshold)[0]
            
            if len(valid_cols) > 0:
                return valid_cols[-1] - valid_cols[0] + 1
            return region.shape[1]
        
        # Dividir cara en 5 secciones
        h1 = int(h * 0.2)  # Frente alta
        h2 = int(h * 0.4)  # Frente-ojos
        h3 = int(h * 0.6)  # Ojos-nariz (MEDIO - importante para Diamante)
        h4 = int(h * 0.8)  # Nariz-boca
        
        forehead_region = gray_face[0:h1, :]
        temple_region = gray_face[h1:h2, :]
        eye_region = gray_face[h2:h3, :]
        cheek_region = gray_face[h3:h4, :]
        jaw_region = gray_face[h4:, :]
        
        # Calcular anchos
        forehead_width = get_width_by_projection(forehead_region, 80)
        temple_width = get_width_by_projection(temple_region, 85)
        eye_width = get_width_by_projection(eye_region, 90)
        cheek_width = get_width_by_projection(cheek_region, 85)
        jaw_width = get_width_by_projection(jaw_region, 80)
        
        # Suavizar medidas
        forehead_width = int((forehead_width * 0.7 + temple_width * 0.3))
        middle_width = int((eye_width * 0.4 + cheek_width * 0.6))
        jaw_width = int((jaw_width * 0.8 + cheek_width * 0.2))
        
        # Detectar ojos
        eyes = self.eye_cascade.detectMultiScale(gray_face, 1.05, 3, minSize=(10, 10))
        eye_distance = 0
        
        if len(eyes) >= 2:
            eyes = sorted(eyes, key=lambda e: e[0])
            eye1_center = eyes[0][0] + eyes[0][2]//2
            eye2_center = eyes[1][0] + eyes[1][2]//2
            eye_distance = abs(eye2_center - eye1_center)
            
            estimated_face_width = eye_distance * 3.2
            if abs(middle_width - estimated_face_width) > face_width * 0.3:
                middle_width = int((middle_width + estimated_face_width) / 2)
        
        # Validar medidas
        max_width = face_width
        forehead_width = min(forehead_width, max_width)
        middle_width = min(middle_width, max_width)
        jaw_width = min(jaw_width, max_width)
        
        min_width = int(face_width * 0.3)
        forehead_width = max(forehead_width, min_width)
        middle_width = max(middle_width, min_width)
        jaw_width = max(jaw_width, min_width)
        
        # Proporciones
        forehead_to_middle_ratio = forehead_width / max(middle_width, 1)
        jaw_to_middle_ratio = jaw_width / max(middle_width, 1)
        forehead_to_jaw_ratio = forehead_width / max(jaw_width, 1)
        
        return {
            'width': face_width,
            'height': face_height,
            'ratio': face_ratio,
            'forehead_width': forehead_width,
            'middle_width': middle_width,
            'jaw_width': jaw_width,
            'eye_distance': eye_distance,
            'forehead_to_middle_ratio': forehead_to_middle_ratio,
            'jaw_to_middle_ratio': jaw_to_middle_ratio,
            'forehead_to_jaw_ratio': forehead_to_jaw_ratio,
            'temple_width': temple_width,
            'cheek_width': cheek_width
        }
    
    def classify_face_shape(self, measurements, contour=None):
        """
        Clasificación en 5 formas: Corazón, Diamante, Ovalado, Redondo, Triangular
        
        DIAMANTE: Pómulos anchos (medio), frente y mandíbula estrechas
        - Medio más ancho que frente y mandíbula
        - Frente estrecha: forehead_to_middle < 0.9
        - Mandíbula estrecha: jaw_to_middle < 0.9
        - Ratio alargado: 1.2 - 1.4
        """
        ratio = measurements['ratio']
        forehead_to_middle = measurements['forehead_to_middle_ratio']
        jaw_to_middle = measurements['jaw_to_middle_ratio']
        forehead_to_jaw = measurements['forehead_to_jaw_ratio']
        
        scores = {
            'Ovalado': 0,
            'Redondo': 0,
            'Corazón': 0,
            'Triangular': 0,
            'Diamante': 0
        }
        
        # CRITERIO 1: Ratio altura/ancho
        if 1.15 <= ratio <= 1.35:  # Ovalado
            scores['Ovalado'] += 3
        elif ratio < 1.05:  # Muy ancha (Redondo)
            scores['Redondo'] += 3
        elif ratio <= 1.15:  # Ligeramente ancha
            scores['Redondo'] += 2
        elif 1.35 < ratio <= 1.5:  # Alargado (puede ser Diamante)
            scores['Diamante'] += 2
            scores['Ovalado'] += 1
        else:  # Muy alargado
            scores['Ovalado'] += 1
        
        # CRITERIO 2: Frente vs Medio
        if forehead_to_middle > 1.15:  # Frente MUY ancha
            scores['Corazón'] += 4
        elif forehead_to_middle > 1.05:  # Frente algo ancha
            scores['Corazón'] += 2
        elif forehead_to_middle < 0.75:  # Frente MUY estrecha (Diamante o Triangular)
            scores['Diamante'] += 3
            scores['Triangular'] += 2
        elif forehead_to_middle < 0.9:  # Frente estrecha (Diamante)
            scores['Diamante'] += 4
            scores['Triangular'] += 1
        else:  # Frente normal
            scores['Ovalado'] += 2
            scores['Redondo'] += 1
        
        # CRITERIO 3: Mandíbula vs Medio
        if jaw_to_middle > 1.15:  # Mandíbula MUY ancha
            scores['Triangular'] += 4
        elif jaw_to_middle > 1.02:  # Mandíbula algo ancha
            scores['Triangular'] += 2
        elif jaw_to_middle < 0.75:  # Mandíbula MUY estrecha (Diamante o Corazón)
            scores['Diamante'] += 3
            scores['Corazón'] += 2
        elif jaw_to_middle < 0.9:  # Mandíbula estrecha (Diamante)
            scores['Diamante'] += 4
            scores['Corazón'] += 1
        else:  # Mandíbula normal
            scores['Ovalado'] += 2
            scores['Redondo'] += 1
        
        # CRITERIO 4: Frente vs Mandíbula
        if forehead_to_jaw > 1.25:  # Frente mucho más ancha
            scores['Corazón'] += 3
        elif forehead_to_jaw < 0.75:  # Mandíbula mucho más ancha
            scores['Triangular'] += 3
        elif 0.95 <= forehead_to_jaw <= 1.05:  # Similares (Diamante o Ovalado)
            scores['Diamante'] += 2
            scores['Ovalado'] += 1
        else:
            scores['Ovalado'] += 1
        
        # CRITERIO 5: Detectar Diamante específicamente
        # Diamante: medio ancho, frente y mandíbula estrechas
        if forehead_to_middle < 0.9 and jaw_to_middle < 0.9:
            scores['Diamante'] += 5  # Bonus fuerte para Diamante
            
            # Si ambos son muy estrechos, es definitivamente Diamante
            if forehead_to_middle < 0.85 and jaw_to_middle < 0.85:
                scores['Diamante'] += 3
        
        # CRITERIO 6: Análisis de contorno
        if contour is not None:
            try:
                hull = cv2.convexHull(contour)
                hull_area = cv2.contourArea(hull)
                contour_area = cv2.contourArea(contour)
                solidity = contour_area / hull_area if hull_area > 0 else 0
                
                if solidity > 0.9:  # Muy suave
                    scores['Redondo'] += 2
                    scores['Ovalado'] += 1
                elif solidity < 0.75:  # Angular (Diamante)
                    scores['Diamante'] += 2
                
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                if len(approx) <= 6:  # Muy angular
                    scores['Diamante'] += 1
                elif len(approx) >= 10:  # Muy suave
                    scores['Redondo'] += 2
                    scores['Ovalado'] += 1
            except:
                pass
        
        # AJUSTES FINALES
        # Diamante con ratio alargado
        if ratio > 1.3 and forehead_to_middle < 0.9 and jaw_to_middle < 0.9:
            scores['Diamante'] += 3
        
        # Redondo: ancho y proporciones similares
        if ratio < 1.1 and abs(forehead_to_jaw - 1.0) < 0.15:
            scores['Redondo'] += 2
        
        # Encontrar mejor forma
        best_shape = max(scores.keys(), key=lambda k: scores[k])
        max_score = scores[best_shape]
        
        # Fallback si puntaje bajo
        if max_score <= 1:
            if ratio > 1.3:
                return "Ovalado"
            elif ratio < 1.1:
                return "Redondo"
            else:
                return "Ovalado"
        
        # Resolver empates
        tied_shapes = [shape for shape, score in scores.items() if score == max_score]
        if len(tied_shapes) > 1:
            if 'Ovalado' in tied_shapes:
                return 'Ovalado'
            elif 'Redondo' in tied_shapes and ratio < 1.15:
                return 'Redondo'
            elif 'Diamante' in tied_shapes:
                return 'Diamante'
            else:
                return tied_shapes[0]
        
        return best_shape
    
    def detect_face_shape(self, image):
        """Detecta la forma de la cara en una imagen"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(50, 50)
        )
        
        results = []
        
        for (x, y, w, h) in faces:
            face_region = image[y:y+h, x:x+w]
            contour, edges = self.analyze_face_contour(face_region)
            measurements = self.calculate_face_measurements(x, y, w, h, face_region)
            face_shape = self.classify_face_shape(measurements, contour)
            
            # Dibujar
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
            
            if contour is not None:
                adjusted_contour = contour.copy()
                adjusted_contour[:, :, 0] += x
                adjusted_contour[:, :, 1] += y
                cv2.drawContours(image, [adjusted_contour], -1, (0, 255, 0), 2)
            
            eyes = self.eye_cascade.detectMultiScale(face_region, 1.1, 5)
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(image, (x + ex, y + ey), (x + ex + ew, y + ey + eh), (0, 255, 255), 2)
            
            cv2.putText(image, f'Forma: {face_shape}', (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            info_lines = [
                f'H/W: {measurements["ratio"]:.2f}',
                f'F:{measurements["forehead_width"]} M:{measurements["middle_width"]} J:{measurements["jaw_width"]}'
            ]
            
            for i, text in enumerate(info_lines):
                cv2.putText(image, text, (x, y + h + 20 + i*15), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
            
            results.append({
                'face_shape': face_shape,
                'measurements': measurements,
                'bbox': (x, y, w, h),
                'contour': contour
            })
        
        return image, results