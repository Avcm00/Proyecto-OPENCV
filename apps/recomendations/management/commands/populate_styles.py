"""
Comando Django para poblar la base de datos con estilos de cortes y barbas.

Ubicación: apps/recomendations/management/commands/populate_styles.py

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
                'suitable_for_shapes': ['oval', 'cuadrado', 'rectangular'],
                'suitable_for_gender': ['hombre'],
                'hair_length_required': ['medio', 'largo'],
                'benefits': [
                    'Fácil de peinar',
                    'Versatil para diferentes ocasiones',
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
                'suitable_for_shapes': ['cuadrado', 'rectangular'],
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
                'suitable_for_shapes': ['cuadrado', 'rectangular', 'oval'],
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
            
            # CORTES PARA ROSTRO RECTANGULAR
            {
                'name': 'Corte con Volumen Lateral',
                'description': 'Cabello con volumen en los lados para ensanchar visualmente. Reduce percepción de longitud.',
                'image_url': '/static/styles/men/side_volume.jpg',
                'suitable_for_shapes': ['rectangular', 'diamante'],
                'suitable_for_gender': ['hombre'],
                'hair_length_required': ['medio'],
                'benefits': [
                    'Ensancha el rostro',
                    'Balancea proporciones',
                    'Natural y versátil',
                    'Fácil mantenimiento'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 78.0,
                'tags': ['natural', 'balanceado', 'versatil']
            },
            {
                'name': 'Flequillo Lateral Largo',
                'description': 'Flequillo largo peinado de lado que acorta visualmente el rostro.',
                'image_url': '/static/styles/men/long_side_fringe.jpg',
                'suitable_for_shapes': ['rectangular', 'corazon'],
                'suitable_for_gender': ['hombre'],
                'hair_length_required': ['medio', 'largo'],
                'benefits': [
                    'Acorta rostro largo',
                    'Estilo artístico',
                    'Moderno y juvenil',
                    'Oculta frente alta'
                ],
                'difficulty_level': 'medio',
                'popularity_score': 80.0,
                'tags': ['artistico', 'moderno', 'juvenil']
            },
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
                'suitable_for_shapes': ['oval', 'redondo', 'rectangular'],
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
                'suitable_for_shapes': ['cuadrado', 'rectangular'],
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
                'suitable_for_shapes': ['cuadrado', 'rectangular', 'diamante'],
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
            
            # CORTES PARA ROSTRO RECTANGULAR
            {
                'name': 'Bob con Flequillo Recto',
                'description': 'Corte bob con flequillo recto que acorta visualmente la frente y el rostro.',
                'image_url': '/static/styles/women/bob_straight_bangs.jpg',
                'suitable_for_shapes': ['rectangular', 'oval'],
                'suitable_for_gender': ['mujer'],
                'hair_length_required': ['medio'],
                'benefits': [
                    'Acorta frente alta',
                    'Reduce largura del rostro',
                    'Estilo definido',
                    'Moderno'
                ],
                'difficulty_level': 'medio',
                'popularity_score': 86.0,
                'tags': ['moderno', 'definido', 'acortador']
            },
            {
                'name': 'Shag con Flequillo Cortina',
                'description': 'Corte en capas despeinadas con flequillo tipo cortina. Da amplitud horizontal.',
                'image_url': '/static/styles/women/shag_curtain.jpg',
                'suitable_for_shapes': ['rectangular', 'diamante'],
                'suitable_for_gender': ['mujer'],
                'hair_length_required': ['medio', 'largo'],
                'benefits': [
                    'Ensancha el rostro',
                    'Estilo desenfadado',
                    'Muy de moda',
                    'Texturizado'
                ],
                'difficulty_level': 'facil',
                'popularity_score': 91.0,
                'tags': ['desenfadado', 'texturizado', 'moda']
            },
        ]
        
        for haircut_data in women_haircuts:
            HaircutStyleModel.objects.create(**haircut_data)
        
        self.stdout.write(self.style.SUCCESS(f'✓ {len(women_haircuts)} cortes para mujeres cargados'))
    
    def load_beard_styles(self):
        """Cargar estilos de barba"""
        beard_styles = [
            {
                'name': 'Barba Completa Cuidada',
                'description': 'Barba completa de longitud media, bien recortada y definida. Clásica y masculina.',
                'image_url': '/static/styles/beards/full_beard.jpg',
                'suitable_for_shapes': ['oval', 'cuadrado', 'rectangular', 'diamante'],
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
                'name': 'Barba de 3 Días',
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
                'popularity_score': 95.0,
                'tags': ['practica', 'corta', 'moderna']
            },
            {
                'name': 'Perilla (Goatee)',
                'description': 'Barba solo en el mentón y área del labio. Alarga el rostro visualmente.',
                'image_url': '/static/styles/beards/goatee.jpg',
                'suitable_for_shapes': ['redondo', 'corazon', 'oval'],
                'benefits': [
                    'Alarga el rostro',
                    'Define mentón',
                    'Estilo distintivo',
                    'Fácil mantenimiento'
                ],
                'maintenance_level': 'medio',
                'popularity_score': 78.0,
                'tags': ['distintiva', 'alargadora', 'definida']
            },
            {
                'name': 'Candado (Van Dyke)',
                'description': 'Combinación de perilla y bigote sin conexión. Estilo sofisticado y distintivo.',
                'image_url': '/static/styles/beards/van_dyke.jpg',
                'suitable_for_shapes': ['corazon', 'triangular', 'oval'],
                'benefits': [
                    'Muy distintivo',
                    'Sofisticado',
                    'Alarga rostro',
                    'Define rasgos'
                ],
                'maintenance_level': 'alto',
                'popularity_score': 72.0,
                'tags': ['sofisticada', 'distintiva', 'elegante']
            },
            {
                'name': 'Barba Redondeada',
                'description': 'Barba completa con bordes redondeados. Suaviza ángulos marcados del rostro.',
                'image_url': '/static/styles/beards/rounded_beard.jpg',
                'suitable_for_shapes': ['cuadrado', 'rectangular'],
                'benefits': [
                    'Suaviza rasgos',
                    'Natural',
                    'Moderna',
                    'Versátil'
                ],
                'maintenance_level': 'medio',
                'popularity_score': 85.0,
                'tags': ['suave', 'natural', 'redondeada']
            },
            {
                'name': 'Barba Angular',
                'description': 'Barba con líneas angulares definidas. Añade estructura al rostro redondo.',
                'image_url': '/static/styles/beards/angular_beard.jpg',
                'suitable_for_shapes': ['redondo', 'oval'],
                'benefits': [
                    'Define mandíbula',
                    'Añade estructura',
                    'Moderna',
                    'Masculina'
                ],
                'maintenance_level': 'alto',
                'popularity_score': 88.0,
                'tags': ['angular', 'definida', 'estructurada']
            },
            {
                'name': 'Barba Corta Lateral',
                'description': 'Barba que sigue la línea de la mandíbula sin cubrir el mentón. Alarga rostro triangular.',
                'image_url': '/static/styles/beards/jawline_beard.jpg',
                'suitable_for_shapes': ['triangular', 'corazon'],
                'benefits': [
                    'Alarga el rostro',
                    'Define mandíbula',
                    'Estilo único',
                    'Bajo volumen'
                ],
                'maintenance_level': 'medio',
                'popularity_score': 75.0,
                'tags': ['unica', 'definida', 'lateral']
            },
            {
                'name': 'Barba Larga Estilizada',
                'description': 'Barba larga y bien cuidada. Muy masculina y de alto impacto visual.',
                'image_url': '/static/styles/beards/long_styled.jpg',
                'suitable_for_shapes': ['oval', 'cuadrado'],
                'benefits': [
                    'Alto impacto',
                    'Muy masculina',
                    'Distintiva',
                    'Llamativa'
                ],
                'maintenance_level': 'alto',
                'popularity_score': 70.0,
                'tags': ['larga', 'impactante', 'distintiva']
            },
        ]
        
        for beard_data in beard_styles:
            BeardStyleModel.objects.create(**beard_data)
        
        self.stdout.write(self.style.SUCCESS(f'✓ {len(beard_styles)} estilos de barba cargados'))