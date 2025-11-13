"""
Casos de uso del módulo de Feedback.
Implementa la lógica de negocio para feedback e historial.
"""

from typing import List, Optional
from datetime import datetime

from .entities import Feedback, AnalysisHistory
from ..ports.repositories import (
    FeedbackRepositoryInterface,
    AnalysisHistoryRepositoryInterface
)


class SaveFeedbackUseCase:
    """
    Caso de uso: Guardar o actualizar feedback de un análisis.
    """
    
    def __init__(self, feedback_repository: FeedbackRepositoryInterface):
        self.feedback_repository = feedback_repository
    
    def execute(
        self,
        user_id: int,
        analysis_id: int,
        rating: int,
        liked: Optional[bool] = None,
        comment: Optional[str] = None
    ) -> Feedback:
        """
        Guarda o actualiza el feedback de un usuario para un análisis.
        """
        existing_feedback = self.feedback_repository.find_by_analysis_id(analysis_id)
        
        if existing_feedback:
            existing_feedback.rating = rating
            existing_feedback.liked = liked
            existing_feedback.comment = comment
            return self.feedback_repository.update(existing_feedback)
        else:
            feedback = Feedback(
                user_id=user_id,
                analysis_id=analysis_id,
                rating=rating,
                liked=liked,
                comment=comment
            )
            return self.feedback_repository.save(feedback)


class GetUserHistoryUseCase:
    """
    Caso de uso: Obtener el historial de análisis de un usuario.
    """
    
    def __init__(self, history_repository: AnalysisHistoryRepositoryInterface):
        self.history_repository = history_repository
    
    def execute(
        self,
        user_id: int,
        limit: int = 10,
        offset: int = 0
    ) -> List[AnalysisHistory]:
        """
        Obtiene el historial de análisis de un usuario con paginación.
        """
        return self.history_repository.find_by_user_id(
            user_id=user_id,
            limit=limit,
            offset=offset
        )


class FilterHistoryUseCase:
    """
    Caso de uso: Filtrar historial según criterios.
    """
    
    def __init__(self, history_repository: AnalysisHistoryRepositoryInterface):
        self.history_repository = history_repository
    
    def filter_by_date(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[AnalysisHistory]:
        """Filtra historial por rango de fechas"""
        return self.history_repository.filter_by_date_range(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
    
    def filter_by_face_shape(
        self,
        user_id: int,
        face_shape: str
    ) -> List[AnalysisHistory]:
        """Filtra historial por forma de rostro"""
        return self.history_repository.filter_by_face_shape(
            user_id=user_id,
            face_shape=face_shape
        )
    
    def filter_by_rating(
        self,
        user_id: int,
        min_rating: int
    ) -> List[AnalysisHistory]:
        """Filtra historial por rating mínimo"""
        return self.history_repository.filter_by_rating(
            user_id=user_id,
            min_rating=min_rating
        )


class GetHistoryStatisticsUseCase:
    """
    Caso de uso: Obtener estadísticas del historial.
    """
    
    def __init__(self, history_repository: AnalysisHistoryRepositoryInterface):
        self.history_repository = history_repository
    
    def execute(self, user_id: int) -> dict:
        """
        Obtiene estadísticas del historial del usuario.
        """
        return self.history_repository.get_statistics(user_id)


class SaveAnalysisToHistoryUseCase:
    """
    Caso de uso: Guardar un análisis en el historial.
    """
    
    def __init__(self, history_repository: AnalysisHistoryRepositoryInterface):
        self.history_repository = history_repository
    
    def execute(
        self,
        user_id: int,
        face_shape: str,
        confidence: float,
        recommendations_count: int,
        pdf_path: Optional[str] = None,
        analysis_data: Optional[dict] = None,
        recommendations_data: Optional[dict] = None
    ) -> AnalysisHistory:
        """
        Guarda un análisis completo en el historial.
        """
        history = AnalysisHistory(
            user_id=user_id,
            face_shape=face_shape,
            confidence=confidence,
            recommendations_count=recommendations_count,
            pdf_path=pdf_path,
            analysis_data=analysis_data,
            recommendations_data=recommendations_data
        )
        
        return self.history_repository.save(history)