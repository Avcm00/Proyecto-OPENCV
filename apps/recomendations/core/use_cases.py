"""
Casos de uso del dominio de recomendaciones.
"""

from typing import List
from .entities import (
    Recommendation, 
    HaircutStyle, 
    BeardStyle,
    FaceShape,
    Gender,
    HairLength
)


class GenerateHaircutRecommendationsUseCase:
    """Genera recomendaciones de cortes de cabello"""
    
    def __init__(self, recommendation_engine, style_catalog):
        self.recommendation_engine = recommendation_engine
        self.style_catalog = style_catalog

    def execute(
        self, 
        face_shape: FaceShape,
        gender: Gender,
        hair_length: HairLength,
        max_results: int = 5
    ) -> List[HaircutStyle]:
        """
        Ejecuta el caso de uso para generar recomendaciones de cortes
        
        Args:
            face_shape: Forma del rostro
            gender: Género del usuario
            hair_length: Longitud actual del cabello
            max_results: Número máximo de resultados
            
        Returns:
            Lista de estilos de corte recomendados
        """
        # Obtener todos los estilos disponibles
        all_styles = self.style_catalog.get_haircut_styles(
            gender=gender,
            hair_length=hair_length
        )
        
        # Filtrar y ordenar por compatibilidad
        recommendations = self.recommendation_engine.rank_haircut_styles(
            styles=all_styles,
            face_shape=face_shape,
            gender=gender,
            hair_length=hair_length
        )
        
        return recommendations[:max_results]


class GenerateBeardRecommendationsUseCase:
    """Genera recomendaciones de estilos de barba"""
    
    def __init__(self, recommendation_engine, style_catalog):
        self.recommendation_engine = recommendation_engine
        self.style_catalog = style_catalog

    def execute(
        self,
        face_shape: FaceShape,
        gender: Gender,
        max_results: int = 5
    ) -> List[BeardStyle]:
        """
        Ejecuta el caso de uso para generar recomendaciones de barba
        
        Args:
            face_shape: Forma del rostro
            gender: Género del usuario
            max_results: Número máximo de resultados
            
        Returns:
            Lista de estilos de barba recomendados
        """
        # Obtener todos los estilos de barba disponibles
        all_styles = self.style_catalog.get_beard_styles(gender=gender)
        
        # Filtrar y ordenar por compatibilidad
        recommendations = self.recommendation_engine.rank_beard_styles(
            styles=all_styles,
            face_shape=face_shape,
            gender=gender
        )
        
        return recommendations[:max_results]


class SaveRecommendationUseCase:
    """Guarda una recomendación en la base de datos"""
    
    def __init__(self, recommendation_repo):
        self.recommendation_repo = recommendation_repo

    def execute(self, recommendation: Recommendation) -> Recommendation:
        """
        Guarda la recomendación en el repositorio
        
        Args:
            recommendation: Recomendación a guardar
            
        Returns:
            Recomendación guardada con ID asignado
        """
        return self.recommendation_repo.save(recommendation)


class GetRecommendationHistoryUseCase:
    """Obtiene el historial de recomendaciones de un usuario"""
    
    def __init__(self, recommendation_repo):
        self.recommendation_repo = recommendation_repo

    def execute(self, user_id: int, limit: int = 10) -> List[Recommendation]:
        """
        Obtiene las últimas recomendaciones del usuario
        
        Args:
            user_id: ID del usuario
            limit: Número máximo de recomendaciones a retornar
            
        Returns:
            Lista de recomendaciones ordenadas por fecha
        """
        return self.recommendation_repo.get_by_user(user_id, limit=limit)