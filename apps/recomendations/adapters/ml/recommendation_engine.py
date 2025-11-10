"""
Motor de recomendaciones basado en reglas y catálogo de estilos.
"""

from typing import List, Dict
from apps.recomendations.core.entities import (
    HaircutStyle,
    BeardStyle,
    FaceShape,
    Gender,
    HairLength
)


class RuleBasedRecommendationEngine:
    """
    Motor de recomendaciones basado en reglas predefinidas
    para cada forma de rostro.
    """
    
    # Reglas de compatibilidad por forma de rostro
    FACE_SHAPE_RULES = {
        FaceShape.OVAL: {
            'haircut_multiplier': 1.2,  # Multiplicador para casi cualquier estilo
            'beard_styles': ['completa', 'corta', 'perilla', 'candado'],
            'tips': [
                'Tu rostro ovalado es versátil y funciona con casi cualquier estilo',
                'Puedes experimentar con diferentes longitudes de cabello',
                'Evita estilos que alarguen demasiado el rostro'
            ]
        },
        FaceShape.REDONDO: {
            'haircut_multiplier': 1.0,
            'beard_styles': ['candado', 'perilla', 'corta_angular'],
            'tips': [
                'Busca estilos que agreguen altura y estructura angular',
                'Los cortes con volumen arriba alargan visualmente el rostro',
                'Evita estilos redondeados que acentúen la forma circular',
                'Las barbas angulares ayudan a definir la mandíbula'
            ]
        },
        FaceShape.CUADRADO: {
            'haircut_multiplier': 1.0,
            'beard_styles': ['completa', 'corta', 'redondeada'],
            'tips': [
                'Suaviza los ángulos con estilos texturizados',
                'Los cortes con movimiento en los laterales funcionan bien',
                'Evita estilos demasiado geométricos o cuadrados',
                'Las barbas redondeadas suavizan la mandíbula fuerte'
            ]
        },
        
        FaceShape.CORAZON: {
            'haircut_multiplier': 1.0,
            'beard_styles': ['perilla', 'candado', 'corta'],
            'tips': [
                'Balancea la frente ancha con volumen en la parte inferior',
                'Los estilos texturizados en los lados funcionan bien',
                'Evita demasiado volumen arriba',
                'Las barbas ayudan a dar peso visual a la mandíbula'
            ]
        },
        FaceShape.DIAMANTE: {
            'haircut_multiplier': 1.0,
            'beard_styles': ['completa', 'perilla', 'media'],
            'tips': [
                'Suaviza los pómulos prominentes con estilos más llenos',
                'Da volumen en la frente y mandíbula',
                'Evita estilos muy apretados en los lados',
                'Las barbas dan amplitud a la mandíbula estrecha'
            ]
        },
        FaceShape.TRIANGULAR: {
            'haircut_multiplier': 1.0,
            'beard_styles': ['perilla', 'candado', 'corta_lateral'],
            'tips': [
                'Balancea la mandíbula ancha con volumen arriba',
                'Los cortes con altura funcionan bien',
                'Evita estilos muy voluminosos en los lados inferiores',
                'Las barbas estilizadas alargan el rostro'
            ]
        }
    }
    
    def rank_haircut_styles(
        self,
        styles: List[HaircutStyle],
        face_shape: FaceShape,
        gender: Gender,
        hair_length: HairLength
    ) -> List[HaircutStyle]:
        """
        Ordena los estilos de corte por compatibilidad
        
        Args:
            styles: Lista de estilos disponibles
            face_shape: Forma del rostro
            gender: Género del usuario
            hair_length: Longitud del cabello
            
        Returns:
            Lista ordenada de estilos más compatibles
        """
        scored_styles = []
        
        for style in styles:
            score = self.calculate_style_score(
                style, face_shape, gender, hair_length
            )
            scored_styles.append((score, style))
        
        # Ordenar por score descendente
        scored_styles.sort(key=lambda x: x[0], reverse=True)
        
        return [style for _, style in scored_styles]
    
    def rank_beard_styles(
        self,
        styles: List[BeardStyle],
        face_shape: FaceShape,
        gender: Gender
    ) -> List[BeardStyle]:
        """
        Ordena los estilos de barba por compatibilidad
        
        Args:
            styles: Lista de estilos disponibles
            face_shape: Forma del rostro
            gender: Género del usuario
            
        Returns:
            Lista ordenada de estilos más compatibles
        """
        scored_styles = []
        
        for style in styles:
            score = self.calculate_beard_score(style, face_shape)
            scored_styles.append((score, style))
        
        # Ordenar por score descendente
        scored_styles.sort(key=lambda x: x[0], reverse=True)
        
        return [style for _, style in scored_styles]
    
    def calculate_style_score(
        self,
        style: HaircutStyle,
        face_shape: FaceShape,
        gender: Gender,
        hair_length: HairLength
    ) -> float:
        """
        Calcula el score de compatibilidad de un estilo de corte
        
        Returns:
            Score entre 0 y 1
        """
        score = 0.0
        
        # Compatibilidad con forma de rostro (peso: 50%)
        if face_shape in style.suitable_for_shapes:
            rules = self.FACE_SHAPE_RULES.get(face_shape, {})
            multiplier = rules.get('haircut_multiplier', 1.0)
            score += 0.5 * multiplier
        
        # Compatibilidad con género (peso: 20%)
        if gender in style.suitable_for_gender:
            score += 0.2
        
        # Compatibilidad con longitud de cabello (peso: 20%)
        if hair_length in style.hair_length_required:
            score += 0.2
        
        # Popularidad (peso: 10%)
        score += 0.1 * (style.popularity_score / 100.0)
        
        return min(score, 1.0)  # Normalizar a máximo 1.0
    
    def calculate_beard_score(
        self,
        style: BeardStyle,
        face_shape: FaceShape
    ) -> float:
        """
        Calcula el score de compatibilidad de un estilo de barba
        
        Returns:
            Score entre 0 y 1
        """
        score = 0.0
        
        # Compatibilidad con forma de rostro (peso: 70%)
        if face_shape in style.suitable_for_shapes:
            score += 0.7
        
        # Popularidad (peso: 30%)
        score += 0.3 * (style.popularity_score / 100.0)
        
        return min(score, 1.0)
    
    def get_face_shape_tips(self, face_shape: FaceShape) -> List[str]:
        """
        Obtiene consejos personalizados para una forma de rostro
        
        Args:
            face_shape: Forma del rostro
            
        Returns:
            Lista de consejos
        """
        rules = self.FACE_SHAPE_RULES.get(face_shape, {})
        return rules.get('tips', [])


class StyleCatalogServiceImpl:
    """
    Servicio para acceder al catálogo de estilos
    """
    
    def __init__(self, style_repository):
        self.style_repository = style_repository
    
    def get_haircut_styles(
        self,
        gender: Gender = None,
        hair_length: HairLength = None,
        face_shape: FaceShape = None
    ) -> List[HaircutStyle]:
        """
        Obtiene estilos de corte del repositorio con filtros
        
        Args:
            gender: Filtro por género
            hair_length: Filtro por longitud de cabello
            face_shape: Filtro por forma de rostro
            
        Returns:
            Lista de estilos de corte
        """
        return self.style_repository.get_haircuts(
            gender=gender,
            hair_length=hair_length,
            face_shape=face_shape
        )
    
    def get_beard_styles(
        self,
        gender: Gender = None,
        face_shape: FaceShape = None
    ) -> List[BeardStyle]:
        """
        Obtiene estilos de barba del repositorio con filtros
        
        Args:
            gender: Filtro por género
            face_shape: Filtro por forma de rostro
            
        Returns:
            Lista de estilos de barba
        """
        return self.style_repository.get_beards(
            gender=gender,
            face_shape=face_shape
        )
    
    def get_haircut_by_id(self, style_id: int) -> HaircutStyle:
        """Obtiene un estilo de corte por ID"""
        return self.style_repository.get_haircut_by_id(style_id)
    
    def get_beard_by_id(self, style_id: int) -> BeardStyle:
        """Obtiene un estilo de barba por ID"""
        return self.style_repository.get_beard_by_id(style_id)