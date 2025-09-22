import cv2
import numpy as np

class FaceShapeDetector:
    def __init__(self):
        # Usar el clasificador Haar Cascade de OpenCV (incluido por defecto)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
    def analyze_face_contour(self, face_region):
        """
        Analiza el contorno de la cara para determinar su forma
        """
        # Convertir a escala de grises
        gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        
        # Aplicar filtros para mejorar la detección de bordes
        blurred = cv2.GaussianBlur(gray_face, (5, 5), 0)
        
        # Detectar bordes usando Canny
        edges = cv2.Canny(blurred, 50, 150)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None, None
        
        # Obtener el contorno más grande (probablemente la cara)
        largest_contour = max(contours, key=cv2.contourArea)
        
        return largest_contour, edges
    
    def calculate_face_measurements(self, x, y, w, h, face_region):
        """
        Calcula medidas usando múltiples métodos para mayor precisión
        """
        gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
        
        # Medidas básicas
        face_width = w
        face_height = h
        face_ratio = face_height / face_width
        
        # Método 1: Análisis por proyección horizontal
        def get_width_by_projection(region, percentile=85):
            if region.size == 0:
                return region.shape[1] if len(region.shape) > 1 else 0
                
            # Proyección horizontal (suma por columnas)
            projection = np.sum(region, axis=0)
            threshold = np.percentile(projection, percentile)
            
            # Encontrar primera y última columna que superen el umbral
            valid_cols = np.where(projection > threshold)[0]
            if len(valid_cols) > 0:
                return valid_cols[-1] - valid_cols[0] + 1
            return region.shape[1]
        
        # Dividir cara en 5 secciones horizontales para análisis más detallado
        h1 = int(h * 0.2)  # Frente alta
        h2 = int(h * 0.4)  # Frente-ojos
        h3 = int(h * 0.6)  # Ojos-nariz
        h4 = int(h * 0.8)  # Nariz-boca
        # h5 = h              # Mandíbula
        
        forehead_region = gray_face[0:h1, :]
        temple_region = gray_face[h1:h2, :]
        eye_region = gray_face[h2:h3, :]
        cheek_region = gray_face[h3:h4, :]
        jaw_region = gray_face[h4:, :]
        
        # Calcular anchos usando proyección
        forehead_width = get_width_by_projection(forehead_region, 80)
        temple_width = get_width_by_projection(temple_region, 85)
        eye_width = get_width_by_projection(eye_region, 90)
        cheek_width = get_width_by_projection(cheek_region, 85)
        jaw_width = get_width_by_projection(jaw_region, 80)
        
        # Suavizar medidas (promedio ponderado con regiones adyacentes)
        forehead_width = int((forehead_width * 0.7 + temple_width * 0.3))
        middle_width = int((eye_width * 0.4 + cheek_width * 0.6))
        jaw_width = int((jaw_width * 0.8 + cheek_width * 0.2))
        
        # Detectar ojos para validación
        eyes = self.eye_cascade.detectMultiScale(gray_face, 1.05, 3, minSize=(10, 10))
        eye_distance = 0
        
        if len(eyes) >= 2:
            eyes = sorted(eyes, key=lambda e: e[0])
            eye1_center = eyes[0][0] + eyes[0][2]//2
            eye2_center = eyes[1][0] + eyes[1][2]//2
            eye_distance = abs(eye2_center - eye1_center)
            
            # Usar distancia entre ojos para corregir ancho medio si es muy diferente
            estimated_face_width = eye_distance * 3.2  # Proporción antropométrica
            if abs(middle_width - estimated_face_width) > face_width * 0.3:
                middle_width = int((middle_width + estimated_face_width) / 2)
        
        # Validar y corregir medidas extremas
        max_width = face_width
        forehead_width = min(forehead_width, max_width)
        middle_width = min(middle_width, max_width)
        jaw_width = min(jaw_width, max_width)
        
        # Asegurar que ningún ancho sea menor al 30% del ancho total
        min_width = int(face_width * 0.3)
        forehead_width = max(forehead_width, min_width)
        middle_width = max(middle_width, min_width)
        jaw_width = max(jaw_width, min_width)
        
        # Calcular proporciones
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
        Clasificación mejorada con múltiples criterios y umbrales calibrados
        """
        ratio = measurements['ratio']
        forehead_to_middle = measurements['forehead_to_middle_ratio']
        jaw_to_middle = measurements['jaw_to_middle_ratio']
        forehead_to_jaw = measurements['forehead_to_jaw_ratio']
        
        # Debug con menos verbosidad
        # print(f"R:{ratio:.2f} F/M:{forehead_to_middle:.2f} J/M:{jaw_to_middle:.2f} F/J:{forehead_to_jaw:.2f}")
        
        # Sistema de puntuación para cada forma
        scores = {
            'Ovalada': 0,
            'Redonda': 0,
            'Cuadrada': 0,
            'Corazón': 0,
            'Triangular': 0,
            'Rectangular': 0
        }
        
        # CRITERIO 1: Ratio altura/ancho
        if 1.1 <= ratio <= 1.35:  # Rango ovalado
            scores['Ovalada'] += 3
        elif ratio > 1.5:  # Muy alargada
            scores['Rectangular'] += 4
            scores['Ovalada'] += 1
        elif ratio < 1.05:  # Muy ancha
            scores['Redonda'] += 3
            scores['Cuadrada'] += 2
        elif ratio <= 1.15:  # Ligeramente ancha
            scores['Redonda'] += 2
            scores['Cuadrada'] += 2
        else:  # Moderadamente alargada
            scores['Ovalada'] += 2
            scores['Rectangular'] += 1
        
        # CRITERIO 2: Frente vs Medio
        if forehead_to_middle > 1.15:  # Frente muy ancha
            scores['Corazón'] += 4
        elif forehead_to_middle > 1.05:  # Frente algo ancha
            scores['Corazón'] += 2
            scores['Triangular'] -= 1
        elif forehead_to_middle < 0.85:  # Frente estrecha
            scores['Triangular'] += 3
            scores['Corazón'] -= 2
        else:  # Frente normal
            scores['Ovalada'] += 1
            scores['Redonda'] += 1
            scores['Cuadrada'] += 1
            scores['Rectangular'] += 1
        
        # CRITERIO 3: Mandíbula vs Medio
        if jaw_to_middle > 1.1:  # Mandíbula muy ancha
            scores['Triangular'] += 4
            scores['Cuadrada'] += 2
        elif jaw_to_middle > 1.02:  # Mandíbula algo ancha
            scores['Cuadrada'] += 2
            scores['Triangular'] += 1
            scores['Rectangular'] += 1
        elif jaw_to_middle < 0.8:  # Mandíbula estrecha
            scores['Corazón'] += 3
            scores['Ovalada'] += 1
        else:  # Mandíbula normal
            scores['Ovalada'] += 2
            scores['Redonda'] += 1
        
        # CRITERIO 4: Frente vs Mandíbula (directo)
        if forehead_to_jaw > 1.2:  # Frente mucho más ancha que mandíbula
            scores['Corazón'] += 3
        elif forehead_to_jaw < 0.8:  # Mandíbula mucho más ancha que frente
            scores['Triangular'] += 3
        else:  # Similares
            scores['Ovalada'] += 1
            scores['Redonda'] += 1
            scores['Cuadrada'] += 1
        
        # CRITERIO 5: Análisis de contorno si está disponible
        if contour is not None:
            try:
                # Calcular convexidad
                hull = cv2.convexHull(contour)
                hull_area = cv2.contourArea(hull)
                contour_area = cv2.contourArea(contour)
                solidity = contour_area / hull_area if hull_area > 0 else 0
                
                if solidity > 0.9:  # Muy suave/convexo
                    scores['Redonda'] += 2
                    scores['Ovalada'] += 1
                elif solidity < 0.8:  # Menos suave, más angular
                    scores['Cuadrada'] += 2
                    scores['Triangular'] += 1
                    scores['Corazón'] += 1
                
                # Aproximar contorno a polígono
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Número de vértices indica angularidad
                if len(approx) <= 6:  # Muy angular
                    scores['Cuadrada'] += 2
                    scores['Triangular'] += 1
                elif len(approx) >= 10:  # Muy suave
                    scores['Redonda'] += 2
                    scores['Ovalada'] += 1
            except:
                pass  # Ignorar errores de contorno
        
        # AJUSTES FINALES: Casos especiales
        # Si es muy alargado pero con mandíbula estrecha, probablemente ovalado
        if ratio > 1.4 and jaw_to_middle < 0.9:
            scores['Ovalada'] += 2
            scores['Rectangular'] -= 1
        
        # Si es ancho pero frente y mandíbula son similares, más probablemente redondo
        if ratio < 1.1 and abs(forehead_to_jaw - 1.0) < 0.15:
            scores['Redonda'] += 2
        
        # Encontrar la forma con mayor puntuación
        best_shape = max(scores.keys(), key=lambda k: scores[k])
        max_score = scores[best_shape]
        
        # Si el puntaje es muy bajo, usar clasificación básica por ratio
        if max_score <= 1:
            if ratio > 1.3:
                return "Ovalada"
            elif ratio < 1.1:
                return "Redonda"
            else:
                return "Ovalada"
        
        # Verificar si hay empate y resolverlo
        tied_shapes = [shape for shape, score in scores.items() if score == max_score]
        if len(tied_shapes) > 1:
            # Desempate usando criterios específicos
            if 'Ovalada' in tied_shapes:
                return 'Ovalada'  # Ovalada es más común
            elif 'Redonda' in tied_shapes and ratio < 1.15:
                return 'Redonda'
            elif 'Cuadrada' in tied_shapes and ratio < 1.2:
                return 'Cuadrada'
            else:
                return tied_shapes[0]
        
        return best_shape
    
    def detect_face_shape(self, image):
        """
        Detecta la forma de la cara en una imagen
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detectar caras
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(50, 50)
        )
        
        results = []
        
        for (x, y, w, h) in faces:
            # Extraer región de la cara
            face_region = image[y:y+h, x:x+w]
            
            # Analizar contorno
            contour, edges = self.analyze_face_contour(face_region)
            
            # Calcular medidas
            measurements = self.calculate_face_measurements(x, y, w, h, face_region)
            
            # Clasificar forma
            face_shape = self.classify_face_shape(measurements, contour)
            
            # Dibujar rectángulo alrededor de la cara
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
            
            # Dibujar contorno si se encontró
            if contour is not None:
                # Ajustar coordenadas del contorno a la imagen completa
                adjusted_contour = contour.copy()
                adjusted_contour[:, :, 0] += x
                adjusted_contour[:, :, 1] += y
                cv2.drawContours(image, [adjusted_contour], -1, (0, 255, 0), 2)
            
            # Dibujar ojos detectados
            eyes = self.eye_cascade.detectMultiScale(face_region, 1.1, 5)
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(image, (x + ex, y + ey), (x + ex + ew, y + ey + eh), (0, 255, 255), 2)
            
            # Añadir texto con la forma detectada
            cv2.putText(image, f'Forma: {face_shape}', (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            # Añadir información detallada más clara
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

def main():
    """
    Función principal para usar con webcam
    """
    detector = FaceShapeDetector()
    cap = cv2.VideoCapture(0)
    
    print("=== DETECTOR DE FORMA DE CARA MEJORADO ===")
    print("Controles:")
    print("- 'q': Salir")
    print("- 's': Guardar screenshot")
    print("- 'i': Mostrar información detallada")
    print("- 'd': Toggle modo debug")
    print("==========================================")
    
    show_debug = False
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo acceder a la cámara")
            break
        
        # Crear copia para procesamiento
        display_frame = frame.copy()
        
        # Detectar forma de cara
        result_frame, face_data = detector.detect_face_shape(display_frame)
        
        # Mostrar información en la imagen
        info_text = f"Caras detectadas: {len(face_data)}"
        cv2.putText(result_frame, info_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Mostrar información de cada cara en consola (cuando se presiona 'i')
        if len(face_data) > 0:
            for i, face_info in enumerate(face_data):
                measurements = face_info['measurements']
                print(f"\n--- Cara {i+1} ---")
                print(f"Forma detectada: {face_info['face_shape']}")
                print(f"Dimensiones: {measurements['width']}x{measurements['height']}")
                print(f"Ratio H/W: {measurements['ratio']:.2f}")
                print(f"Frente/Medio: {measurements['forehead_to_middle_ratio']:.2f}")
                print(f"Mandíbula/Medio: {measurements['jaw_to_middle_ratio']:.2f}")
                print(f"Anchos - Frente: {measurements['forehead_width']}, Medio: {measurements['middle_width']}, Mandíbula: {measurements['jaw_width']}")
        
        # Mostrar resultado
        cv2.imshow('Detector de Forma de Cara - Mejorado', result_frame)
        
        # Controles mejorados
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = 'face_detection_result.jpg'
            cv2.imwrite(filename, result_frame)
            print(f"Screenshot guardado como: {filename}")
        elif key == ord('i'):
            # Mostrar información detallada
            if len(face_data) > 0:
                print("\n" + "="*50)
                for i, face_info in enumerate(face_data):
                    measurements = face_info['measurements']
                    print(f"\n--- CARA {i+1} ---")
                    print(f"Forma detectada: {face_info['face_shape']}")
                    print(f"Dimensiones: {measurements['width']}x{measurements['height']}")
                    print(f"Ratio H/W: {measurements['ratio']:.2f}")
                    print(f"Anchos - Frente:{measurements['forehead_width']}, Medio:{measurements['middle_width']}, Mandíbula:{measurements['jaw_width']}")
                    print(f"Proporciones - F/M:{measurements['forehead_to_middle_ratio']:.2f}, J/M:{measurements['jaw_to_middle_ratio']:.2f}, F/J:{measurements['forehead_to_jaw_ratio']:.2f}")
                print("="*50)
        elif key == ord('d'):
            show_debug = not show_debug
            print(f"Modo debug: {'ON' if show_debug else 'OFF'}")
    
    cap.release()
    cv2.destroyAllWindows()

def process_image(image_path):
    """
    Procesa una imagen desde archivo
    """
    detector = FaceShapeDetector()
    
    # Cargar imagen
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: No se pudo cargar la imagen: {image_path}")
        return
    
    print(f"Procesando imagen: {image_path}")
    
    # Detectar forma de cara
    result_image, face_data = detector.detect_face_shape(image.copy())
    
    # Mostrar resultados en consola
    print(f"\n=== RESULTADOS ===")
    print(f"Caras detectadas: {len(face_data)}")
    
    for i, face_info in enumerate(face_data):
        print(f"\n--- Cara {i+1} ---")
        print(f"Forma: {face_info['face_shape']}")
        print(f"Dimensiones: {face_info['measurements']['width']}x{face_info['measurements']['height']}")
        print(f"Ratio alto/ancho: {face_info['measurements']['ratio']:.2f}")
        print(f"Posición: x={face_info['bbox'][0]}, y={face_info['bbox'][1]}")
    
    # Mostrar imagen
    cv2.imshow('Resultado - Presiona cualquier tecla para cerrar', result_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # Guardar resultado
    output_path = f"resultado_{image_path}"
    cv2.imwrite(output_path, result_image)
    print(f"\nResultado guardado como: {output_path}")

if __name__ == "__main__":
    print("Selecciona una opción:")
    print("1. Usar webcam (tiempo real)")
    print("2. Procesar imagen específica")
    
    try:
        opcion = input("Ingresa 1 o 2: ").strip()
        
        if opcion == "1":
            main()
        elif opcion == "2":
            ruta = input("Ingresa la ruta de la imagen: ").strip()
            process_image(ruta)
        else:
            print("Opción no válida")
    except KeyboardInterrupt:
        print("\nPrograma terminado por el usuario")
    except Exception as e:
        print(f"Error: {e}")