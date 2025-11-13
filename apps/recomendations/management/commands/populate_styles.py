"""tengo una carpeta en media donde estan precargados las imagenes estan en una subcarpeta llamada beards para los estilos de barba y haircuts_image para los cortes de cabello quiero usar esas imagenes precargadas
Comando Django para poblar la base de datos con estilos de cortes y barbas.
Compatible con los modelos HaircutStyleModel y BeardStyleModel proporcionados.
NOTA: Todos los 'popularity_score' han sido escalados para un máximo de 10.0.
"""
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files import File 
from apps.recomendations.models import (
    HaircutStyleModel,
    BeardStyleModel
)

# --- RUTAS IMPORTANTES (CORREGIDO) ---
# Define la ruta base que apunta a la raíz del proyecto.
# Ahora, las rutas de las imágenes en los diccionarios deben comenzar con '' o 'static/'.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Navega 4 niveles arriba para llegar a la raíz del proyecto (asumiendo: app/management/commands/file.py)
BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# --- FIN RUTAS IMPORTANTES ---


class Command(BaseCommand):
    help = 'Poblar la base de datos con estilos de cortes y barbas iniciales'

    def handle(self, *args, **kwargs):
        self.stdout.write('Iniciando carga de estilos...')
        
        # Limpiar datos existentes (opcional)
        if self.confirm_action('¿Deseas eliminar los estilos existentes?'):
            HaircutStyleModel.objects.all().delete()
            BeardStyleModel.objects.all().delete()
            self.stdout.write(self.style.WARNING('Estilos existentes eliminados'))
        
        self.stdout.write(self.style.NOTICE('--- CARGANDO CORTES DE CABELLO ---'))
        self.load_men_haircuts()
        self.load_women_haircuts()
        
        self.stdout.write(self.style.NOTICE('--- CARGANDO ESTILOS DE BARBA ---'))
        self.load_beard_styles()
        
        self.stdout.write(self.style.SUCCESS('\n✓ Carga de datos inicial completada exitosamente'))
    
    def confirm_action(self, message):
        """Solicitar confirmación del usuario"""
        response = input(f"{message} (s/n): ")
        return response.lower() == 's'
    
    def _create_style_with_image(self, Model, data):
        data_to_save = data.copy()

        # Obtener ruta completa de la imagen
        image_relative_path = data_to_save.pop('image').strip('/')  # ej: 'haircuts/quiff.png'
        image_full_path = os.path.join(settings.BASE_DIR, 'media', image_relative_path)

        if not os.path.exists(image_full_path):
            self.stdout.write(self.style.ERROR(f"✖ Archivo no encontrado: {image_full_path}"))
            return

        try:
            style_instance = Model(**data_to_save)
            with open(image_full_path, 'rb') as f:
                style_instance.image.save(os.path.basename(image_full_path), File(f), save=False)
                style_instance.save()
            self.stdout.write(f"  > Creado: {data.get('name', 'Estilo sin nombre')} ({Model.__name__})")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✖ Error al crear {data.get('name', 'Estilo')}: {e}"))
            

    def load_men_haircuts(self):
        """Cargar estilos de corte para hombres (gender='men')"""
        # Se ha cambiado la ruta de las imágenes a 'haircuts/...'
        men_haircuts = [
            {
                'name': 'Undercut Clásico',
                'description': 'Corte versátil con laterales muy cortos y volumen arriba. Ideal para looks modernos y profesionales.',
                'image': 'haircuts/undercut_clasico.png',
                'suitable_for_shapes': ['oval', 'cuadrado'],
                'gender': 'men',
                'hair_length_required': ['medio', 'largo'],
                'benefits': [
                    'Fácil de peinar',
                    'Versátil para diferentes ocasiones',
                    'Resalta rasgos masculinos',
                    'Bajo mantenimiento en laterales'
                ],
                'difficulty_level': 'medio',
                'popularity_score': 9.5, # Ajustado de 95.0
                'tags': ['moderno', 'profesional', 'versatil']
            },
            {
                'name': 'Pompadour Moderno',
                'description': 'Corte con gran volumen frontal y laterales degradados. Estilo retro-moderno con mucha personalidad.',
                'image': 'haircuts/pompadour.png',
                'suitable_for_shapes': ['oval', 'redondo', 'corazon'],
                'gender': 'men',
                'hair_length_required': ['medio', 'largo'],
                'benefits': [
                    'Alarga el rostro visualmente',
                    'Estilo elegante y sofisticado',
                    'Gran impacto visual',
                    'Oculta frente amplia'
                ],
                'difficulty_level': 'dificil',
                'popularity_score': 8.8, # Ajustado de 88.0
                'tags': ['elegante', 'retro', 'voluminoso']
            },
            {
                'name': 'Buzz Cut (Rapado)',
                'description': 'Corte muy corto uniforme. Minimalista, masculino y de mantenimiento casi nulo.',
                'image': 'haircuts/buzz_cut.png',
                'suitable_for_shapes': ['oval', 'cuadrado'],
                'gender': 'men',
                'hair_length_required': ['corto'],
                'benefits': [
                    'Cero mantenimiento',
                    'Muy práctico',
                    'Resalta estructura facial',
                    'Ideal para clima cálido'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 7.5, # Ajustado de 75.0
                'tags': ['minimalista', 'practico', 'deportivo']
            },
            {
                'name': 'Quiff Alto',
                'description': 'Corte con gran altura frontal que alarga visualmente el rostro. Laterales cortos con transición.',
                'image': 'haircuts/quiff.png',
                'suitable_for_shapes': ['redondo', 'corazon'],
                'gender': 'men',
                'hair_length_required': ['medio'],
                'benefits': [
                    'Alarga el rostro',
                    'Añade estructura angular',
                    'Estilo moderno',
                    'Versátil para peinar'
                ],
                'difficulty_level': 'medio',
                'popularity_score': 9.0, # Ajustado de 90.0
                'tags': ['moderno', 'angular', 'estructurado']
            },
            {
                'name': 'Fade Alto Texturizado',
                'description': 'Degradado alto con textura en la parte superior. Crea líneas verticales que alargan.',
                'image': 'haircuts/high_fade.png',
                'suitable_for_shapes': ['redondo', 'oval'],
                'gender': 'men',
                'hair_length_required': ['corto', 'medio'],
                'benefits': [
                    'Efecto alargador',
                    'Muy moderno',
                    'Define la forma del rostro',
                    'Bajo mantenimiento'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 9.2, # Ajustado de 92.0
                'tags': ['moderno', 'deportivo', 'definido']
            },
            {
                'name': 'Crop Texturizado',
                'description': 'Corte corto con flequillo frontal texturizado. Suaviza ángulos marcados del rostro.',
                'image': 'haircuts/textured_crop.png',
                'suitable_for_shapes': ['cuadrado'],
                'gender': 'men',
                'hair_length_required': ['corto', 'medio'],
                'benefits': [
                    'Suaviza rasgos angulares',
                    'Muy de moda',
                    'Fácil mantenimiento',
                    'Versátil casual-formal'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 8.9, # Ajustado de 89.0
                'tags': ['casual', 'texturizado', 'moderno']
            },
            {
                'name': 'Side Part Clásico',
                'description': 'Raya lateral definida con peinado hacia un lado. Estilo elegante que suaviza ángulos.',
                'image': 'haircuts/side_part.png',
                'suitable_for_shapes': ['cuadrado', 'oval'],
                'gender': 'men',
                'hair_length_required': ['medio'],
                'benefits': [
                    'Muy elegante',
                    'Profesional',
                    'Suaviza mandíbula fuerte',
                    'Clásico atemporal'
                ],
                'difficulty_level': 'medio',
                'popularity_score': 8.5, # Ajustado de 85.0
                'tags': ['clasico', 'elegante', 'profesional']
            },
            {
                'name': 'Slick Back Medio',
                'description': 'Cabello peinado hacia atrás con volumen moderado. Balancea frente amplia.',
                'image': 'haircuts/slick_back.png',
                'suitable_for_shapes': ['corazon', 'triangular', 'oval'],
                'gender': 'men',
                'hair_length_required': ['medio', 'largo'],
                'benefits': [
                    'Balancea proporciones',
                    'Muy elegante',
                    'Sofisticado',
                    'Oculta frente amplia'
                ],
                'difficulty_level': 'medio',
                'popularity_score': 8.2, # Ajustado de 82.0
                'tags': ['elegante', 'sofisticado', 'volumen']
            },
            {
                'name': 'Fringe Despeinado',
                'description': 'Flequillo frontal con textura despeinada. Reduce visualmente la frente.',
                'image': 'haircuts/messy_fringe.png',
                'suitable_for_shapes': ['corazon', 'diamante'],
                'gender': 'men',
                'hair_length_required': ['medio'],
                'benefits': [
                    'Reduce frente amplia',
                    'Estilo juvenil',
                    'Casual y relajado',
                    'Fácil de peinar'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 8.6, # Ajustado de 86.0
                'tags': ['casual', 'juvenil', 'despeinado']
            },
            {
                'name': 'Taper Fade Clásico',
                'description': 'Degradado gradual desde arriba hacia abajo. Limpio y profesional.',
                'image': 'haircuts/taper_fade.png',
                'suitable_for_shapes': ['oval', 'redondo', 'cuadrado'],
                'gender': 'men',
                'hair_length_required': ['corto', 'medio'],
                'benefits': [
                    'Muy limpio',
                    'Profesional',
                    'Bajo mantenimiento',
                    'Universal'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 9.4, # Ajustado de 94.0
                'tags': ['clasico', 'limpio', 'profesional']
            },
            {
                'name': 'Man Bun',
                'description': 'Cabello largo recogido en moño. Estilo relajado y moderno para cabello largo.',
                'image': 'haircuts/man_bun.png',
                'suitable_for_shapes': ['oval', 'triangular'],
                'gender': 'men',
                'hair_length_required': ['largo'],
                'benefits': [
                    'Estilo único',
                    'Práctico para cabello largo',
                    'Moderno',
                    'Versátil'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 7.8, # Ajustado de 78.0
                'tags': ['moderno', 'largo', 'practico']
            },
            {
                'name': 'Crew Cut Militar',
                'description': 'Corte corto militar con ligera transición. Muy masculino y práctico.',
                'image': 'haircuts/crew_cut.png',
                'suitable_for_shapes': ['oval', 'cuadrado', 'diamante'],
                'gender': 'men',
                'hair_length_required': ['corto'],
                'benefits': [
                    'Muy masculino',
                    'Cero mantenimiento',
                    'Profesional',
                    'Atemporal'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 8.0, # Ajustado de 80.0
                'tags': ['militar', 'corto', 'masculino']
            }
        ]
        
        for haircut_data in men_haircuts:
            self._create_style_with_image(HaircutStyleModel, haircut_data)
        
        self.stdout.write(self.style.SUCCESS(f'✓ {len(men_haircuts)} cortes para hombres cargados'))
    
    def load_women_haircuts(self):
        """Cargar estilos de corte para mujeres (gender='women')"""
        # Se ha cambiado la ruta de las imágenes a 'haircuts/...'
        women_haircuts = [
            {
                'name': 'Long Bob (Lob)',
                'description': 'Corte a la altura de los hombros, versátil y elegante. Funciona con cualquier forma de rostro.',
                'image': 'haircuts/lob.png',
                'suitable_for_shapes': ['oval', 'redondo', 'cuadrado'],
                'gender': 'women',
                'hair_length_required': ['medio', 'largo'],
                'benefits': [
                    'Muy versátil',
                    'Fácil de mantener',
                    'Elegante y moderno',
                    'Funciona con cualquier textura'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 9.5, # Ajustado de 95.0
                'tags': ['versatil', 'elegante', 'moderno']
            },
            {
                'name': 'Pixie Clásico',
                'description': 'Corte muy corto y femenino. Resalta rasgos faciales y cuello. Requiere mantenimiento frecuente.',
                'image': 'haircuts/pixie.png',
                'suitable_for_shapes': ['oval', 'corazon'],
                'gender': 'women',
                'hair_length_required': ['corto'],
                'benefits': [
                    'Muy práctico',
                    'Resalta rasgos',
                    'Juvenil y atrevido',
                    'Refrescante'
                ],
                'difficulty_level': 'medio',
                'popularity_score': 8.2, # Ajustado de 82.0
                'tags': ['practico', 'atrevido', 'juvenil']
            },
            {
                'name': 'Capas Largas',
                'description': 'Cabello largo con capas que dan movimiento y volumen. Favorecedor y femenino.',
                'image': 'haircuts/long_layers.png',
                'suitable_for_shapes': ['oval', 'redondo'],
                'gender': 'women',
                'hair_length_required': ['largo'],
                'benefits': [
                    'Añade movimiento',
                    'Da volumen',
                    'Muy femenino',
                    'Fácil de peinar'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 9.3, # Ajustado de 93.0
                'tags': ['femenino', 'movimiento', 'volumen']
            },
            {
                'name': 'Bob Asimétrico',
                'description': 'Corte bob con un lado más largo que el otro. Crea líneas angulares que alargan el rostro.',
                'image': 'haircuts/asymmetric_bob.png',
                'suitable_for_shapes': ['redondo', 'cuadrado'],
                'gender': 'women',
                'hair_length_required': ['corto', 'medio'],
                'benefits': [
                    'Alarga el rostro',
                    'Muy moderno',
                    'Angular y definido',
                    'Llamativo'
                ],
                'difficulty_level': 'medio',
                'popularity_score': 8.8, # Ajustado de 88.0
                'tags': ['moderno', 'angular', 'atrevido']
            },
            {
                'name': 'Ondas Largas con Raya Lateral',
                'description': 'Cabello largo ondulado con raya profunda a un lado. Las líneas verticales alargan.',
                'image': 'haircuts/long_waves_side.png',
                'suitable_for_shapes': ['redondo', 'corazon'],
                'gender': 'women',
                'hair_length_required': ['largo'],
                'benefits': [
                    'Efecto alargador',
                    'Romántico y femenino',
                    'Enmarca el rostro',
                    'Versátil'
                ],
                'difficulty_level': 'medio',
                'popularity_score': 9.0, # Ajustado de 90.0
                'tags': ['romantico', 'femenino', 'ondulado']
            },
            {
                'name': 'Bob Ondulado Suave',
                'description': 'Corte bob con ondas suaves que suavizan ángulos marcados de la mandíbula.',
                'image': 'haircuts/wavy_bob.png',
                'suitable_for_shapes': ['cuadrado'],
                'gender': 'women',
                'hair_length_required': ['medio'],
                'benefits': [
                    'Suaviza rasgos angulares',
                    'Elegante',
                    'Fácil de mantener',
                    'Muy femenino'
                ],
                'difficulty_level': 'medio',
                'popularity_score': 8.7, # Ajustado de 87.0
                'tags': ['suave', 'elegante', 'femenino']
            },
            {
                'name': 'Capas Medias con Flequillo',
                'description': 'Cabello en capas a altura media con flequillo lateral. Suaviza mandíbula fuerte.',
                'image': 'haircuts/layered_bangs.png',
                'suitable_for_shapes': ['cuadrado', 'diamante'],
                'gender': 'women',
                'hair_length_required': ['medio'],
                'benefits': [
                    'Suaviza ángulos',
                    'Enmarca el rostro',
                    'Versátil',
                    'Fácil de peinar'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 8.5, # Ajustado de 85.0
                'tags': ['versatil', 'enmarcador', 'suave']
            },
            {
                'name': 'Bob Chin-Length',
                'description': 'Corte bob justo a la altura del mentón. Da peso visual a la parte inferior del rostro.',
                'image': 'haircuts/chin_bob.png',
                'suitable_for_shapes': ['corazon', 'triangular'],
                'gender': 'women',
                'hair_length_required': ['medio'],
                'benefits': [
                    'Balancea frente amplia',
                    'Da peso al mentón',
                    'Elegante',
                    'Fácil mantenimiento'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 8.9, # Ajustado de 89.0
                'tags': ['balanceado', 'elegante', 'definido']
            },
            {
                'name': 'Ondas con Volumen Bajo',
                'description': 'Cabello ondulado con más volumen en la parte inferior. Balancea frente ancha.',
                'image': 'haircuts/bottom_volume_waves.png',
                'suitable_for_shapes': ['corazon', 'diamante'],
                'gender': 'women',
                'hair_length_required': ['medio', 'largo'],
                'benefits': [
                    'Balancea proporciones',
                    'Romántico',
                    'Femenino',
                    'Natural'
                ],
                'difficulty_level': 'medio',
                'popularity_score': 8.4, # Ajustado de 84.0
                'tags': ['romantico', 'balanceado', 'natural']
            },
            {
                'name': 'Shag Moderno',
                'description': 'Corte en capas desiguales con textura. Estilo desenfadado y juvenil.',
                'image': 'haircuts/modern_shag.png',
                'suitable_for_shapes': ['oval', 'redondo', 'corazon'],
                'gender': 'women',
                'hair_length_required': ['medio', 'largo'],
                'benefits': [
                    'Muy de moda',
                    'Añade volumen',
                    'Juvenil',
                    'Fácil de peinar'
                ],
                'difficulty_level': 'medio',
                'popularity_score': 9.1, # Ajustado de 91.0
                'tags': ['moderno', 'texturizado', 'juvenil']
            },
            {
                'name': 'Curtain Bangs',
                'description': 'Flequillo en forma de cortina que enmarca el rostro. Muy favorecedor.',
                'image': 'haircuts/curtain_bangs.png',
                'suitable_for_shapes': ['oval', 'redondo', 'corazon'],
                'gender': 'women',
                'hair_length_required': ['medio', 'largo'],
                'benefits': [
                    'Enmarca el rostro',
                    'Muy favorecedor',
                    'Romántico',
                    'Versátil'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 9.2, # Ajustado de 92.0
                'tags': ['romantico', 'enmarcador', 'trendy']
            },
            {
                'name': 'Blunt Bob',
                'description': 'Bob recto sin capas, corte limpio y definido. Sofisticado y elegante.',
                'image': 'haircuts/blunt_bob.png',
                'suitable_for_shapes': ['oval', 'cuadrado', 'diamante'],
                'gender': 'women',
                'hair_length_required': ['medio'],
                'benefits': [
                    'Muy sofisticado',
                    'Líneas limpias',
                    'Elegante',
                    'Moderno'
                ],
                'difficulty_level': 'medio',
                'popularity_score': 8.6, # Ajustado de 86.0
                'tags': ['sofisticado', 'limpio', 'elegante']
            }
        ]
        
        for haircut_data in women_haircuts:
            self._create_style_with_image(HaircutStyleModel, haircut_data)
        
        self.stdout.write(self.style.SUCCESS(f'✓ {len(women_haircuts)} cortes para mujeres cargados'))
    
    def load_beard_styles(self):
        """Cargar estilos de barba"""
        # Se ha cambiado la ruta de las imágenes a 'beards/...'
        beard_styles = [
            # ESTILOS CLÁSICOS
            {
                'name': 'Barba Completa Cuidada',
                'description': 'Barba completa de longitud media, bien recortada y definida. Clásica y masculina.',
                'image': 'beards/full_beard.png',
                'suitable_for_shapes': ['oval', 'cuadrado', 'diamante'],
                'benefits': [
                    'Muy masculina',
                    'Define mandíbula',
                    'Versátil',
                    'Oculta imperfecciones'
                ],
                'maintenance_level': 'medio',
                'difficulty_level': 'medio',
                'popularity_score': 9.2, # Ajustado de 92.0
                'tags': ['clasica', 'masculina', 'completa']
            },
            {
                'name': 'Barba de 3 Días (Stubble)',
                'description': 'Barba corta y uniforme, también conocida como "stubble". Masculina con bajo mantenimiento.',
                'image': 'beards/stubble.png',
                'suitable_for_shapes': ['oval', 'cuadrado', 'redondo'],
                'benefits': [
                    'Bajo mantenimiento',
                    'Masculina',
                    'Moderna',
                    'Muy práctica'
                ],
                'maintenance_level': 'bajo',
                'difficulty_level': 'facil',
                'popularity_score': 9.4, # Ajustado de 94.0
                'tags': ['moderna', 'corta', 'practica']
            },
            
            # ESTILOS PROFESIONALES
            {
                'name': 'Barba Corporate',
                'description': 'Barba corta muy bien cuidada ideal para ambientes profesionales.',
                'image': 'beards/corporate.png',
                'suitable_for_shapes': ['oval', 'cuadrado', 'redondo'],
                'benefits': [
                    'Muy profesional',
                    'Pulcra',
                    'Conservadora',
                    'Aceptada en empresas'
                ],
                'maintenance_level': 'medio',
                'difficulty_level': 'medio',
                'popularity_score': 8.7, # Ajustado de 87.0
                'tags': ['profesional', 'corporativa', 'pulcra']
            },
            {
                'name': 'Barba Van Dyke',
                'description': 'Combinación de perilla y bigote sin conexión. Sofisticada y distinguida.',
                'image': 'beards/van_dyke.png',
                'suitable_for_shapes': ['redondo', 'oval', 'corazon'],
                'benefits': [
                    'Sofisticada',
                    'Distinguida',
                    'Alarga el rostro',
                    'Clásica'
                ],
                'maintenance_level': 'medio',
                'difficulty_level': 'dificil',
                'popularity_score': 7.9, # Ajustado de 79.0
                'tags': ['sofisticada', 'clasica', 'distinguida']
            },
            
            # ESTILOS MINIMALISTAS
            {
                'name': 'Barba de Sombra',
                'description': 'Barba muy corta, apenas visible. Minimalista y moderna.',
                'image': 'beards/shadow.png',
                'suitable_for_shapes': ['oval', 'redondo', 'cuadrado', 'corazon'],
                'benefits': [
                    'Muy bajo mantenimiento',
                    'Minimalista',
                    'Natural',
                    'Universal'
                ],
                'maintenance_level': 'bajo',
                'difficulty_level': 'facil',
                'popularity_score': 8.9, # Ajustado de 89.0
                'tags': ['minimalista', 'natural', 'sutil']
            },
            {
                'name': 'Perilla Extendida',
                'description': 'Perilla que se extiende por la línea de la mandíbula. Define y alarga.',
                'image': 'beards/extended_goatee.png',
                'suitable_for_shapes': ['redondo', 'corazon', 'triangular'],
                'benefits': [
                    'Define mandíbula',
                    'Alarga el rostro',
                    'Moderna',
                    'Versátil'
                ],
                'maintenance_level': 'medio',
                'difficulty_level': 'medio',
                'popularity_score': 8.1, # Ajustado de 81.0
                'tags': ['moderna', 'definida', 'alargadora']
            },
            
            # ESTILOS CREATIVOS
            {
                'name': 'Barba Ducktail',
                'description': 'Barba con forma de cola de pato en el mentón. Característica y moderna.',
                'image': 'beards/ducktail.png',
                'suitable_for_shapes': ['oval', 'redondo', 'cuadrado'],
                'benefits': [
                    'Muy característica',
                    'Moderna',
                    'Alarga el rostro',
                    'Distinguida'
                ],
                'maintenance_level': 'alto',
                'difficulty_level': 'dificil',
                'popularity_score': 7.7, # Ajustado de 77.0
                'tags': ['caracteristica', 'moderna', 'estructurada']
            },
            {
                'name': 'Barba Verdi',
                'description': 'Barba redondeada con bigote separado y curvado. Sofisticada estilo italiano.',
                'image': 'beards/verdi.png',
                'suitable_for_shapes': ['oval', 'triangular'],
                'benefits': [
                    'Muy sofisticada',
                    'Italiana',
                    'Elegante',
                    'Única'
                ],
                'maintenance_level': 'alto',
                'difficulty_level': 'dificil',
                'popularity_score': 7.3, # Ajustado de 73.0
                'tags': ['sofisticada', 'italiana', 'elegante']
            },
            
            # ESTILOS DEPORTIVOS
            {
                'name': 'Barba Deportiva',
                'description': 'Barba corta uniforme ideal para deportistas. Práctica y masculina.',
                'image': 'beards/athletic.png',
                'suitable_for_shapes': ['oval', 'cuadrado', 'redondo'],
                'benefits': [
                    'Muy práctica',
                    'Deportiva',
                    'Bajo mantenimiento',
                    'Masculina'
                ],
                'maintenance_level': 'bajo',
                'difficulty_level': 'facil',
                'popularity_score': 8.6, # Ajustado de 86.0
                'tags': ['deportiva', 'practica', 'corta']
            },
            {
                'name': 'Barba Recortada Uniforme',
                'description': 'Barba muy uniforme en toda la cara. Limpia y ordenada.',
                'image': 'beards/uniform_trim.png',
                'suitable_for_shapes': ['oval', 'cuadrado', 'diamante'],
                'benefits': [
                    'Muy ordenada',
                    'Limpia',
                    'Profesional',
                    'Fácil mantenimiento'
                ],
                'maintenance_level': 'medio',
                'difficulty_level': 'medio',
                'popularity_score': 8.4, # Ajustado de 84.0
                'tags': ['ordenada', 'limpia', 'uniforme']
            },
            
            # ESTILOS HÍBRIDOS
            {
                'name': 'Barba con Patillas Conectadas',
                'description': 'Barba que se conecta completamente con las patillas. Cobertura total.',
                'image': 'beards/full_sideburns.png',
                'suitable_for_shapes': ['oval', 'triangular', 'diamante'],
                'benefits': [
                    'Cobertura completa',
                    'Masculina',
                    'Define contornos',
                    'Versatil'
                ],
                'maintenance_level': 'medio',
                'difficulty_level': 'medio',
                'popularity_score': 8.2, # Ajustado de 82.0
                'tags': ['completa', 'definida', 'masculina']
            },
            {
                'name': 'Barba Garibaldi',
                'description': 'Barba ancha y redondeada en la base. Natural con carácter.',
                'image': 'beards/garibaldi.png',
                'suitable_for_shapes': ['oval', 'triangular'],
                'benefits': [
                    'Natural',
                    'Característica',
                    'Masculina',
                    'Imponente'
                ],
                'maintenance_level': 'medio',
                'difficulty_level': 'medio',
                'popularity_score': 7.5, # Ajustado de 75.0
                'tags': ['natural', 'ancha', 'caracteristica']
            },
            
            # ESTILOS URBANOS
            {
                'name': 'Barba Hipster',
                'description': 'Barba abundante con bigote bien cuidado. Estilo urbano y atrevido.',
                'image': 'beards/hipster.png',
                'suitable_for_shapes': ['oval', 'triangular'],
                'benefits': [
                    'Muy de moda',
                    'Atrevida',
                    'Imponente',
                    'Añade carácter'
                ],
                'maintenance_level': 'alto',
                'difficulty_level': 'dificil',
                'popularity_score': 8.5, # Ajustado de 85.0
                'tags': ['urbana', 'atrevida', 'larga']
            }
        ]
        
        for beard_data in beard_styles:
            self._create_style_with_image(BeardStyleModel, beard_data)
        
        self.stdout.write(self.style.SUCCESS(f'✓ {len(beard_styles)} estilos de barba cargados'))