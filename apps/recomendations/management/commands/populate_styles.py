"""
Comando Django para poblar la base de datos con estilos de cortes y barbas.

Ubicación: apps/recommendations/management/commands/populate_styles.py

Ejecutar con: python manage.py populate_styles
"""

from django.core.management.base import BaseCommand
from apps.recomendations.models import (
    HaircutStyleModel,
    BeardStyleModel
)


class Command(BaseCommand):
    help = 'Poblar la base de datos con estilos de cortes y barbas iniciales'

    def handle(self, *args, **kwargs):
        self.stdout.write('Iniciando carga de estilos...')
        
        # Limpiar datos existentes (opcional)
        if self.confirm_action('¿Deseas eliminar los estilos existentes?'):
            HaircutStyleModel.objects.all().delete()
            BeardStyleModel.objects.all().delete()
            self.stdout.write(self.style.WARNING('Estilos existentes eliminados'))
        
        # Cargar estilos de corte para hombres
        self.load_men_haircuts()
        
        # Cargar estilos de corte para mujeres
        self.load_women_haircuts()
        
        # Cargar estilos de barba
        self.load_beard_styles()
        
        self.stdout.write(self.style.SUCCESS('✓ Estilos cargados exitosamente'))
    
    def confirm_action(self, message):
        """Solicitar confirmación del usuario"""
        response = input(f"{message} (s/n): ")
        return response.lower() == 's'
    
    def load_men_haircuts(self):
        """Cargar estilos de corte para hombres"""
        men_haircuts = [
            # CORTES PARA ROSTRO OVAL
            {
                'name': 'Undercut Clásico',
                'description': 'Corte versátil con laterales muy cortos y volumen arriba. Ideal para looks modernos y profesionales.',
                'image_url': '/static/styles/men/undercut_clasico.jpg',
                'suitable_for_shapes': ['oval', 'cuadrado'],
                'suitable_for_gender': ['hombre'],
                'hair_length_required': ['medio', 'largo'],
                'benefits': [
                    'Fácil de peinar',
                    'Versátil para diferentes ocasiones',
                    'Resalta rasgos masculinos',
                    'Bajo mantenimiento en laterales'
                ],
                'difficulty_level': 'medio',
                'popularity_score': 95.0,
                'tags': ['moderno', 'profesional', 'versatil']
            },
            {
                'name': 'Pompadour Moderno',
                'description': 'Corte con gran volumen frontal y laterales degradados. Estilo retro-moderno con mucha personalidad.',
                'image_url': '/static/styles/men/pompadour.jpg',
                'suitable_for_shapes': ['oval', 'redondo', 'corazon'],
                'suitable_for_gender': ['hombre'],
                'hair_length_required': ['medio', 'largo'],
                'benefits': [
                    'Alarga el rostro visualmente',
                    'Estilo elegante y sofisticado',
                    'Gran impacto visual',
                    'Oculta frente amplia'
                ],
                'difficulty_level': 'dificil',
                'popularity_score': 88.0,
                'tags': ['elegante', 'retro', 'voluminoso']
            },
            {
                'name': 'Buzz Cut (Rapado)',
                'description': 'Corte muy corto uniforme. Minimalista, masculino y de mantenimiento casi nulo.',
                'image_url': '/static/styles/men/buzz_cut.jpg',
                'suitable_for_shapes': ['oval', 'cuadrado'],
                'suitable_for_gender': ['hombre'],
                'hair_length_required': ['corto'],
                'benefits': [
                    'Cero mantenimiento',
                    'Muy práctico',
                    'Resalta estructura facial',
                    'Ideal para clima cálido'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 75.0,
                'tags': ['minimalista', 'practico', 'deportivo']
            },
            
            # CORTES PARA ROSTRO REDONDO
            {
                'name': 'Quiff Alto',
                'description': 'Corte con gran altura frontal que alarga visualmente el rostro. Laterales cortos con transición.',
                'image_url': '/static/styles/men/quiff.jpg',
                'suitable_for_shapes': ['redondo', 'corazon'],
                'suitable_for_gender': ['hombre'],
                'hair_length_required': ['medio'],
                'benefits': [
                    'Alarga el rostro',
                    'Añade estructura angular',
                    'Estilo moderno',
                    'Versátil para peinar'
                ],
                'difficulty_level': 'medio',
                'popularity_score': 90.0,
                'tags': ['moderno', 'angular', 'estructurado']
            },
            {
                'name': 'Fade Alto Texturizado',
                'description': 'Degradado alto con textura en la parte superior. Crea líneas verticales que alargan.',
                'image_url': '/static/styles/men/high_fade.jpg',
                'suitable_for_shapes': ['redondo', 'oval'],
                'suitable_for_gender': ['hombre'],
                'hair_length_required': ['corto', 'medio'],
                'benefits': [
                    'Efecto alargador',
                    'Muy moderno',
                    'Define la forma del rostro',
                    'Bajo mantenimiento'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 92.0,
                'tags': ['moderno', 'deportivo', 'definido']
            },
            
            # CORTES PARA ROSTRO CUADRADO
            {
                'name': 'Crop Texturizado',
                'description': 'Corte corto con flequillo frontal texturizado. Suaviza ángulos marcados del rostro.',
                'image_url': '/static/styles/men/textured_crop.jpg',
                'suitable_for_shapes': ['cuadrado'],
                'suitable_for_gender': ['hombre'],
                'hair_length_required': ['corto', 'medio'],
                'benefits': [
                    'Suaviza rasgos angulares',
                    'Muy de moda',
                    'Fácil mantenimiento',
                    'Versátil casual-formal'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 89.0,
                'tags': ['casual', 'texturizado', 'moderno']
            },
            {
                'name': 'Side Part Clásico',
                'description': 'Raya lateral definida con peinado hacia un lado. Estilo elegante que suaviza ángulos.',
                'image_url': '/static/styles/men/side_part.jpg',
                'suitable_for_shapes': ['cuadrado', 'oval'],
                'suitable_for_gender': ['hombre'],
                'hair_length_required': ['medio'],
                'benefits': [
                    'Muy elegante',
                    'Profesional',
                    'Suaviza mandíbula fuerte',
                    'Clásico atemporal'
                ],
                'difficulty_level': 'medio',
                'popularity_score': 85.0,
                'tags': ['clasico', 'elegante', 'profesional']
            },
            
            # CORTES PARA ROSTRO CORAZÓN
            {
                'name': 'Slick Back Medio',
                'description': 'Cabello peinado hacia atrás con volumen moderado. Balancea frente amplia.',
                'image_url': '/static/styles/men/slick_back.jpg',
                'suitable_for_shapes': ['corazon', 'triangular', 'oval'],
                'suitable_for_gender': ['hombre'],
                'hair_length_required': ['medio', 'largo'],
                'benefits': [
                    'Balancea proporciones',
                    'Muy elegante',
                    'Sofisticado',
                    'Oculta frente amplia'
                ],
                'difficulty_level': 'medio',
                'popularity_score': 82.0,
                'tags': ['elegante', 'sofisticado', 'volumen']
            },
            {
                'name': 'Fringe Despeinado',
                'description': 'Flequillo frontal con textura despeinada. Reduce visualmente la frente.',
                'image_url': '/static/styles/men/messy_fringe.jpg',
                'suitable_for_shapes': ['corazon', 'diamante'],
                'suitable_for_gender': ['hombre'],
                'hair_length_required': ['medio'],
                'benefits': [
                    'Reduce frente amplia',
                    'Estilo juvenil',
                    'Casual y relajado',
                    'Fácil de peinar'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 86.0,
                'tags': ['casual', 'juvenil', 'despeinado']
            },
            
            # CORTES ADICIONALES VERSÁTILES
            {
                'name': 'Taper Fade Clásico',
                'description': 'Degradado gradual desde arriba hacia abajo. Limpio y profesional.',
                'image_url': '/static/styles/men/taper_fade.jpg',
                'suitable_for_shapes': ['oval', 'redondo', 'cuadrado'],
                'suitable_for_gender': ['hombre'],
                'hair_length_required': ['corto', 'medio'],
                'benefits': [
                    'Muy limpio',
                    'Profesional',
                    'Bajo mantenimiento',
                    'Universal'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 94.0,
                'tags': ['clasico', 'limpio', 'profesional']
            },
            {
                'name': 'Man Bun',
                'description': 'Cabello largo recogido en moño. Estilo relajado y moderno para cabello largo.',
                'image_url': '/static/styles/men/man_bun.jpg',
                'suitable_for_shapes': ['oval', 'triangular'],
                'suitable_for_gender': ['hombre'],
                'hair_length_required': ['largo'],
                'benefits': [
                    'Estilo único',
                    'Práctico para cabello largo',
                    'Moderno',
                    'Versátil'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 78.0,
                'tags': ['moderno', 'largo', 'practico']
            },
            {
                'name': 'Crew Cut Militar',
                'description': 'Corte corto militar con ligera transición. Muy masculino y práctico.',
                'image_url': '/static/styles/men/crew_cut.jpg',
                'suitable_for_shapes': ['oval', 'cuadrado', 'diamante'],
                'suitable_for_gender': ['hombre'],
                'hair_length_required': ['corto'],
                'benefits': [
                    'Muy masculino',
                    'Cero mantenimiento',
                    'Profesional',
                    'Atemporal'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 80.0,
                'tags': ['militar', 'corto', 'masculino']
            }
        ]
        
        for haircut_data in men_haircuts:
            HaircutStyleModel.objects.create(**haircut_data)
        
        self.stdout.write(self.style.SUCCESS(f'✓ {len(men_haircuts)} cortes para hombres cargados'))
    
    def load_women_haircuts(self):
        """Cargar estilos de corte para mujeres"""
        women_haircuts = [
            # CORTES PARA ROSTRO OVAL
            {
                'name': 'Long Bob (Lob)',
                'description': 'Corte a la altura de los hombros, versátil y elegante. Funciona con cualquier forma de rostro.',
                'image_url': '/static/styles/women/lob.jpg',
                'suitable_for_shapes': ['oval', 'redondo', 'cuadrado'],
                'suitable_for_gender': ['mujer'],
                'hair_length_required': ['medio', 'largo'],
                'benefits': [
                    'Muy versátil',
                    'Fácil de mantener',
                    'Elegante y moderno',
                    'Funciona con cualquier textura'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 95.0,
                'tags': ['versatil', 'elegante', 'moderno']
            },
            {
                'name': 'Pixie Clásico',
                'description': 'Corte muy corto y femenino. Resalta rasgos faciales y cuello. Requiere mantenimiento frecuente.',
                'image_url': '/static/styles/women/pixie.jpg',
                'suitable_for_shapes': ['oval', 'corazon'],
                'suitable_for_gender': ['mujer'],
                'hair_length_required': ['corto'],
                'benefits': [
                    'Muy práctico',
                    'Resalta rasgos',
                    'Juvenil y atrevido',
                    'Refrescante'
                ],
                'difficulty_level': 'medio',
                'popularity_score': 82.0,
                'tags': ['practico', 'atrevido', 'juvenil']
            },
            {
                'name': 'Capas Largas',
                'description': 'Cabello largo con capas que dan movimiento y volumen. Favorecedor y femenino.',
                'image_url': '/static/styles/women/long_layers.jpg',
                'suitable_for_shapes': ['oval', 'redondo'],
                'suitable_for_gender': ['mujer'],
                'hair_length_required': ['largo'],
                'benefits': [
                    'Añade movimiento',
                    'Da volumen',
                    'Muy femenino',
                    'Fácil de peinar'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 93.0,
                'tags': ['femenino', 'movimiento', 'volumen']
            },
            
            # CORTES PARA ROSTRO REDONDO
            {
                'name': 'Bob Asimétrico',
                'description': 'Corte bob con un lado más largo que el otro. Crea líneas angulares que alargan el rostro.',
                'image_url': '/static/styles/women/asymmetric_bob.jpg',
                'suitable_for_shapes': ['redondo', 'cuadrado'],
                'suitable_for_gender': ['mujer'],
                'hair_length_required': ['corto', 'medio'],
                'benefits': [
                    'Alarga el rostro',
                    'Muy moderno',
                    'Angular y definido',
                    'Llamativo'
                ],
                'difficulty_level': 'medio',
                'popularity_score': 88.0,
                'tags': ['moderno', 'angular', 'atrevido']
            },
            {
                'name': 'Ondas Largas con Raya Lateral',
                'description': 'Cabello largo ondulado con raya profunda a un lado. Las líneas verticales alargan.',
                'image_url': '/static/styles/women/long_waves_side.jpg',
                'suitable_for_shapes': ['redondo', 'corazon'],
                'suitable_for_gender': ['mujer'],
                'hair_length_required': ['largo'],
                'benefits': [
                    'Efecto alargador',
                    'Romántico y femenino',
                    'Enmarca el rostro',
                    'Versátil'
                ],
                'difficulty_level': 'medio',
                'popularity_score': 90.0,
                'tags': ['romantico', 'femenino', 'ondulado']
            },
            
            # CORTES PARA ROSTRO CUADRADO
            {
                'name': 'Bob Ondulado Suave',
                'description': 'Corte bob con ondas suaves que suavizan ángulos marcados de la mandíbula.',
                'image_url': '/static/styles/women/wavy_bob.jpg',
                'suitable_for_shapes': ['cuadrado'],
                'suitable_for_gender': ['mujer'],
                'hair_length_required': ['medio'],
                'benefits': [
                    'Suaviza rasgos angulares',
                    'Elegante',
                    'Fácil de mantener',
                    'Muy femenino'
                ],
                'difficulty_level': 'medio',
                'popularity_score': 87.0,
                'tags': ['suave', 'elegante', 'femenino']
            },
            {
                'name': 'Capas Medias con Flequillo',
                'description': 'Cabello en capas a altura media con flequillo lateral. Suaviza mandíbula fuerte.',
                'image_url': '/static/styles/women/layered_bangs.jpg',
                'suitable_for_shapes': ['cuadrado', 'diamante'],
                'suitable_for_gender': ['mujer'],
                'hair_length_required': ['medio'],
                'benefits': [
                    'Suaviza ángulos',
                    'Enmarca el rostro',
                    'Versátil',
                    'Fácil de peinar'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 85.0,
                'tags': ['versatil', 'enmarcador', 'suave']
            },
            
            # CORTES PARA ROSTRO CORAZÓN
            {
                'name': 'Bob Chin-Length',
                'description': 'Corte bob justo a la altura del mentón. Da peso visual a la parte inferior del rostro.',
                'image_url': '/static/styles/women/chin_bob.jpg',
                'suitable_for_shapes': ['corazon', 'triangular'],
                'suitable_for_gender': ['mujer'],
                'hair_length_required': ['medio'],
                'benefits': [
                    'Balancea frente amplia',
                    'Da peso al mentón',
                    'Elegante',
                    'Fácil mantenimiento'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 89.0,
                'tags': ['balanceado', 'elegante', 'definido']
            },
            {
                'name': 'Ondas con Volumen Bajo',
                'description': 'Cabello ondulado con más volumen en la parte inferior. Balancea frente ancha.',
                'image_url': '/static/styles/women/bottom_volume_waves.jpg',
                'suitable_for_shapes': ['corazon', 'diamante'],
                'suitable_for_gender': ['mujer'],
                'hair_length_required': ['medio', 'largo'],
                'benefits': [
                    'Balancea proporciones',
                    'Romántico',
                    'Femenino',
                    'Natural'
                ],
                'difficulty_level': 'medio',
                'popularity_score': 84.0,
                'tags': ['romantico', 'balanceado', 'natural']
            },
            
            # CORTES ADICIONALES VERSÁTILES
            {
                'name': 'Shag Moderno',
                'description': 'Corte en capas desiguales con textura. Estilo desenfadado y juvenil.',
                'image_url': '/static/styles/women/modern_shag.jpg',
                'suitable_for_shapes': ['oval', 'redondo', 'corazon'],
                'suitable_for_gender': ['mujer'],
                'hair_length_required': ['medio', 'largo'],
                'benefits': [
                    'Muy de moda',
                    'Añade volumen',
                    'Juvenil',
                    'Fácil de peinar'
                ],
                'difficulty_level': 'medio',
                'popularity_score': 91.0,
                'tags': ['moderno', 'texturizado', 'juvenil']
            },
            {
                'name': 'Curtain Bangs',
                'description': 'Flequillo en forma de cortina que enmarca el rostro. Muy favorecedor.',
                'image_url': '/static/styles/women/curtain_bangs.jpg',
                'suitable_for_shapes': ['oval', 'redondo', 'corazon'],
                'suitable_for_gender': ['mujer'],
                'hair_length_required': ['medio', 'largo'],
                'benefits': [
                    'Enmarca el rostro',
                    'Muy favorecedor',
                    'Romántico',
                    'Versátil'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 92.0,
                'tags': ['romantico', 'enmarcador', 'trendy']
            },
            {
                'name': 'Blunt Bob',
                'description': 'Bob recto sin capas, corte limpio y definido. Sofisticado y elegante.',
                'image_url': '/static/styles/women/blunt_bob.jpg',
                'suitable_for_shapes': ['oval', 'cuadrado', 'diamante'],
                'suitable_for_gender': ['mujer'],
                'hair_length_required': ['medio'],
                'benefits': [
                    'Muy sofisticado',
                    'Líneas limpias',
                    'Elegante',
                    'Moderno'
                ],
                'difficulty_level': 'medio',
                'popularity_score': 86.0,
                'tags': ['sofisticado', 'limpio', 'elegante']
            }
        ]
        
        for haircut_data in women_haircuts:
            HaircutStyleModel.objects.create(**haircut_data)
        
        self.stdout.write(self.style.SUCCESS(f'✓ {len(women_haircuts)} cortes para mujeres cargados'))
    
    def load_beard_styles(self):
        """Cargar estilos de barba"""
        beard_styles = [
            # ESTILOS CLÁSICOS
            {
                'name': 'Barba Completa Cuidada',
                'description': 'Barba completa de longitud media, bien recortada y definida. Clásica y masculina.',
                'image_url': '/static/styles/beards/full_beard.jpg',
                'suitable_for_shapes': ['oval', 'cuadrado', 'diamante'],
                'benefits': [
                    'Muy masculina',
                    'Define mandíbula',
                    'Versátil',
                    'Oculta imperfecciones'
                ],
                'maintenance_level': 'medio',
                'popularity_score': 92.0,
                'tags': ['clasica', 'masculina', 'completa']
            },
            {
                'name': 'Barba de 3 Días (Stubble)',
                'description': 'Barba corta y uniforme, también conocida como "stubble". Masculina con bajo mantenimiento.',
                'image_url': '/static/styles/beards/stubble.jpg',
                'suitable_for_shapes': ['oval', 'cuadrado', 'redondo'],
                'benefits': [
                    'Bajo mantenimiento',
                    'Masculina',
                    'Moderna',
                    'Muy práctica'
                ],
                'maintenance_level': 'bajo',
                'popularity_score': 74.0,
                'tags': ['clasico', 'bigote', 'retro']
            },
            
            # ESTILOS PROFESIONALES
            {
                'name': 'Barba Corporate',
                'description': 'Barba corta muy bien cuidada ideal para ambientes profesionales.',
                'image_url': '/static/styles/beards/corporate.jpg',
                'suitable_for_shapes': ['oval', 'cuadrado', 'redondo'],
                'benefits': [
                    'Muy profesional',
                    'Pulcra',
                    'Conservadora',
                    'Aceptada en empresas'
                ],
                'maintenance_level': 'medio',
                'popularity_score': 87.0,
                'tags': ['profesional', 'corporativa', 'pulcra']
            },
            {
                'name': 'Barba Van Dyke',
                'description': 'Combinación de perilla y bigote sin conexión. Sofisticada y distinguida.',
                'image_url': '/static/styles/beards/van_dyke.jpg',
                'suitable_for_shapes': ['redondo', 'oval', 'corazon'],
                'benefits': [
                    'Sofisticada',
                    'Distinguida',
                    'Alarga el rostro',
                    'Clásica'
                ],
                'maintenance_level': 'medio',
                'popularity_score': 79.0,
                'tags': ['sofisticada', 'clasica', 'distinguida']
            },
            
            # ESTILOS MINIMALISTAS
            {
                'name': 'Barba de Sombra',
                'description': 'Barba muy corta, apenas visible. Minimalista y moderna.',
                'image_url': '/static/styles/beards/shadow.jpg',
                'suitable_for_shapes': ['oval', 'redondo', 'cuadrado', 'corazon'],
                'benefits': [
                    'Muy bajo mantenimiento',
                    'Minimalista',
                    'Natural',
                    'Universal'
                ],
                'maintenance_level': 'bajo',
                'popularity_score': 89.0,
                'tags': ['minimalista', 'natural', 'sutil']
            },
            {
                'name': 'Perilla Extendida',
                'description': 'Perilla que se extiende por la línea de la mandíbula. Define y alarga.',
                'image_url': '/static/styles/beards/extended_goatee.jpg',
                'suitable_for_shapes': ['redondo', 'corazon', 'triangular'],
                'benefits': [
                    'Define mandíbula',
                    'Alarga el rostro',
                    'Moderna',
                    'Versátil'
                ],
                'maintenance_level': 'medio',
                'popularity_score': 81.0,
                'tags': ['moderna', 'definida', 'alargadora']
            },
            
            # ESTILOS CREATIVOS
            {
                'name': 'Barba Ducktail',
                'description': 'Barba con forma de cola de pato en el mentón. Característica y moderna.',
                'image_url': '/static/styles/beards/ducktail.jpg',
                'suitable_for_shapes': ['oval', 'redondo', 'cuadrado'],
                'benefits': [
                    'Muy característica',
                    'Moderna',
                    'Alarga el rostro',
                    'Distinguida'
                ],
                'maintenance_level': 'alto',
                'popularity_score': 77.0,
                'tags': ['caracteristica', 'moderna', 'estructurada']
            },
            {
                'name': 'Barba Verdi',
                'description': 'Barba redondeada con bigote separado y curvado. Sofisticada estilo italiano.',
                'image_url': '/static/styles/beards/verdi.jpg',
                'suitable_for_shapes': ['oval', 'triangular'],
                'benefits': [
                    'Muy sofisticada',
                    'Italiana',
                    'Elegante',
                    'Única'
                ],
                'maintenance_level': 'alto',
                'popularity_score': 73.0,
                'tags': ['sofisticada', 'italiana', 'elegante']
            },
            
            # ESTILOS DEPORTIVOS
            {
                'name': 'Barba Deportiva',
                'description': 'Barba corta uniforme ideal para deportistas. Práctica y masculina.',
                'image_url': '/static/styles/beards/athletic.jpg',
                'suitable_for_shapes': ['oval', 'cuadrado', 'redondo'],
                'benefits': [
                    'Muy práctica',
                    'Deportiva',
                    'Bajo mantenimiento',
                    'Masculina'
                ],
                'maintenance_level': 'bajo',
                'popularity_score': 86.0,
                'tags': ['deportiva', 'practica', 'corta']
            },
            {
                'name': 'Barba Recortada Uniforme',
                'description': 'Barba muy uniforme en toda la cara. Limpia y ordenada.',
                'image_url': '/static/styles/beards/uniform_trim.jpg',
                'suitable_for_shapes': ['oval', 'cuadrado', 'diamante'],
                'benefits': [
                    'Muy ordenada',
                    'Limpia',
                    'Profesional',
                    'Fácil mantenimiento'
                ],
                'maintenance_level': 'medio',
                'popularity_score': 84.0,
                'tags': ['ordenada', 'limpia', 'uniforme']
            },
            
            # ESTILOS HÍBRIDOS
            {
                'name': 'Barba con Patillas Conectadas',
                'description': 'Barba que se conecta completamente con las patillas. Cobertura total.',
                'image_url': '/static/styles/beards/full_sideburns.jpg',
                'suitable_for_shapes': ['oval', 'triangular', 'diamante'],
                'benefits': [
                    'Cobertura completa',
                    'Masculina',
                    'Define contornos',
                    'Versatil'
                ],
                'maintenance_level': 'medio',
                'popularity_score': 82.0,
                'tags': ['completa', 'definida', 'masculina']
            },
            {
                'name': 'Barba Garibaldi',
                'description': 'Barba ancha y redondeada en la base. Natural con carácter.',
                'image_url': '/static/styles/beards/garibaldi.jpg',
                'suitable_for_shapes': ['oval', 'triangular'],
                'benefits': [
                    'Natural',
                    'Característica',
                    'Masculina',
                    'Imponente'
                ],
                'maintenance_level': 'medio',
                'popularity_score': 75.0,
                'tags': ['natural', 'ancha', 'caracteristica']
            },
            
            # ESTILOS URBANOS
            {
                'name': 'Barba Hipster',
                'description': 'Barba abundante con bigote bien cuidado. Estilo urbano moderno.',
                'image_url': '/static/styles/beards/hipster.jpg',
                'suitable_for_shapes': ['oval', 'redondo', 'corazon'],
                'benefits': [
                    'Muy de moda',
                    'Urbana',
                    'Característica',
                    'Moderna'
                ],
                'maintenance_level': 'alto',
                'popularity_score': 80.0,
                'tags': ['hipster', 'urbana', 'moderna']
            },
            {
                'name': 'Barba Lumberjack',
                'description': 'Barba abundante y natural estilo leñador. Masculina y rústica.',
                'image_url': '/static/styles/beards/lumberjack.jpg',
                'suitable_for_shapes': ['oval', 'cuadrado'],
                'benefits': [
                    'Muy masculina',
                    'Natural',
                    'Rústica',
                    'Abundante'
                ],
                'maintenance_level': 'medio',
                'popularity_score': 78.0,
                'tags': ['rustica', 'masculina', 'abundante']
            },
            
            # ESTILOS BALANCEADOS
            {
                'name': 'Barba Balbo',
                'description': 'Barba sin patillas con bigote desconectado. Balanceada y única.',
                'image_url': '/static/styles/beards/balbo.jpg',
                'suitable_for_shapes': ['redondo', 'oval', 'diamante'],
                'benefits': [
                    'Muy característica',
                    'Balanceada',
                    'Define mentón',
                    'Moderna'
                ],
                'maintenance_level': 'alto',
                'popularity_score': 76.0,
                'tags': ['caracteristica', 'balanceada', 'unica']
            },
            {
                'name': 'Barba Anchor',
                'description': 'Barba con forma de ancla en el mentón. Distintiva y definida.',
                'image_url': '/static/styles/beards/anchor.jpg',
                'suitable_for_shapes': ['redondo', 'corazon'],
                'benefits': [
                    'Muy distintiva',
                    'Define mentón',
                    'Alarga el rostro',
                    'Moderna'
                ],
                'maintenance_level': 'medio',
                'popularity_score': 72.0,
                'tags': ['distintiva', 'definida', 'moderna']
            },
            
            # ESTILOS CONSERVADORES
            {
                'name': 'Barba Corta Clásica',
                'description': 'Barba corta tradicional sin diseños elaborados. Atemporal.',
                'image_url': '/static/styles/beards/classic_short.jpg',
                'suitable_for_shapes': ['oval', 'cuadrado', 'redondo', 'corazon'],
                'benefits': [
                    'Atemporal',
                    'Conservadora',
                    'Profesional',
                    'Universal'
                ],
                'maintenance_level': 'bajo',
                'popularity_score': 88.0,
                'tags': ['clasica', 'atemporal', 'conservadora']
            },
            {
                'name': 'Barba Friendly Mutton Chops',
                'description': 'Patillas anchas conectadas por bigote. Retro y característica.',
                'image_url': '/static/styles/beards/mutton_chops.jpg',
                'suitable_for_shapes': ['oval', 'triangular'],
                'benefits': [
                    'Muy característica',
                    'Retro',
                    'Única',
                    'Vintage'
                ],
                'maintenance_level': 'alto',
                'popularity_score': 68.0,
                'tags': ['retro', 'caracteristica', 'vintage']
            }
        ]
        
        for beard_data in beard_styles:
            BeardStyleModel.objects.create(**beard_data)
        
        self.stdout.write(self.style.SUCCESS(f'✓ {len(beard_styles)} estilos de barba cargados')) 
           
        beard_styles = [
            {
                'name': 'Perilla (Goatee)',
                'description': 'Barba solo en mentón y bigote. Estilo clásico que alarga el rostro.',
                'image_url': '/static/styles/beards/goatee.jpg',
                'suitable_for_shapes': ['redondo', 'corazon', 'diamante'],
                'benefits': [
                    'Alarga el rostro',
                    'Bajo mantenimiento',
                    'Clásica',
                    'Define mentón'
                ],
                'maintenance_level': 'bajo',
                'popularity_score': 78.0,
                'tags': ['clasica', 'definida', 'minimalista']
            },
            
            # ESTILOS MODERNOS
            {
                'name': 'Barba Desvanecida (Fade Beard)',
                'description': 'Barba con degradado que se desvanece hacia las patillas. Muy moderna y estilizada.',
                'image_url': '/static/styles/beards/fade_beard.jpg',
                'suitable_for_shapes': ['oval', 'redondo', 'cuadrado'],
                'benefits': [
                    'Muy moderna',
                    'Estilizada',
                    'Define contornos',
                    'Sofisticada'
                ],
                'maintenance_level': 'alto',
                'popularity_score': 88.0,
                'tags': ['moderna', 'estilizada', 'fade']
            },
            {
                'name': 'Barba Corta Definida',
                'description': 'Barba corta con líneas bien definidas. Pulcra y profesional.',
                'image_url': '/static/styles/beards/short_defined.jpg',
                'suitable_for_shapes': ['oval', 'cuadrado', 'triangular'],
                'benefits': [
                    'Muy profesional',
                    'Pulcra',
                    'Fácil mantenimiento',
                    'Define mandíbula'
                ],
                'maintenance_level': 'medio',
                'popularity_score': 90.0,
                'tags': ['profesional', 'definida', 'corta']
            },
            
            # ESTILOS PARA FORMAS ESPECÍFICAS
            {
                'name': 'Barba Cuadrada',
                'description': 'Barba con forma cuadrada que añade estructura a rostros redondos.',
                'image_url': '/static/styles/beards/square_beard.jpg',
                'suitable_for_shapes': ['redondo', 'oval'],
                'benefits': [
                    'Añade ángulos',
                    'Define mandíbula',
                    'Masculina',
                    'Estructurada'
                ],
                'maintenance_level': 'medio',
                'popularity_score': 85.0,
                'tags': ['estructurada', 'angular', 'definida']
            },
            {
                'name': 'Barba Redondeada',
                'description': 'Barba con líneas redondeadas que suaviza rostros angulares.',
                'image_url': '/static/styles/beards/rounded_beard.jpg',
                'suitable_for_shapes': ['cuadrado', 'diamante'],
                'benefits': [
                    'Suaviza ángulos',
                    'Equilibrada',
                    'Natural',
                    'Versátil'
                ],
                'maintenance_level': 'medio',
                'popularity_score': 83.0,
                'tags': ['suave', 'equilibrada', 'natural']
            },
            
            # ESTILOS LARGOS
            {
                'name': 'Barba Larga Viking',
                'description': 'Barba larga y abundante estilo vikingo. Requiere alto mantenimiento pero muy característica.',
                'image_url': '/static/styles/beards/viking_beard.jpg',
                'suitable_for_shapes': ['oval', 'triangular'],
                'benefits': [
                    'Muy característica',
                    'Masculina',
                    'Única',
                    'Imponente'
                ],
                'maintenance_level': 'alto',
                'popularity_score': 72.0,
                'tags': ['larga', 'viking', 'caracteristica']
            },
            {
                'name': 'Barba Bandholz',
                'description': 'Barba larga natural con bigote. Estilo relajado y bohemio.',
                'image_url': '/static/styles/beards/bandholz.jpg',
                'suitable_for_shapes': ['oval', 'triangular', 'diamante'],
                'benefits': [
                    'Natural',
                    'Bohemia',
                    'Característica',
                    'Versatile'
                ],
                'maintenance_level': 'alto',
                'popularity_score': 76.0,
                'tags': ['larga', 'natural', 'bohemia']
            },
            
            # ESTILOS CON BIGOTE
            {
                'name': 'Barba con Bigote Manubrio',
                'description': 'Barba corta con bigote estilo manubrio. Vintage y sofisticado.',
                'image_url': '/static/styles/beards/handlebar.jpg',
                'suitable_for_shapes': ['oval', 'corazon'],
                'benefits': [
                    'Muy característica',
                    'Vintage',
                    'Sofisticada',
                    'Única'
                ],
                'maintenance_level': 'alto',
                'popularity_score': 70.0,
                'tags': ['vintage', 'bigote', 'caracteristica']
            },
            {
                'name': 'Barba con Bigote Chevron',
                'description': 'Barba corta con bigote grueso estilo chevron. Masculina y clásica.',
                'image_url': '/static/styles/beards/chevron.jpg',
                'suitable_for_shapes': ['oval', 'cuadrado', 'redondo'],
                'benefits': [
                    'Masculina',
                    'Clásica',
                    'Define rostro',
                    'Fácil mantenimiento'
                ],
                'maintenance_level': 'medio',
                'popularity_score': 82.0,
                'tags': ['clasica', 'masculina', 'definida']
            }
        ]
        