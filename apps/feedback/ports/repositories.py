"""
Interfaces (puertos) para los repositorios de Feedback.
Define los contratos que deben cumplir las implementaciones.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from ..core.entities import Feedback, AnalysisHistory


class FeedbackRepositoryInterface(ABC):
    """
    Interface para el repositorio de Feedback.
    """
    
    @abstractmethod
    def save(self, feedback: Feedback) -> Feedback:
        """Guarda un nuevo feedback"""
        pass
    
    @abstractmethod
    def find_by_analysis_id(self, analysis_id: int) -> Optional[Feedback]:
        """Busca feedback por ID de análisis"""
        pass
    
    @abstractmethod
    def find_by_user_id(self, user_id: int) -> List[Feedback]:
        """Obtiene todos los feedbacks de un usuario"""
        pass
    
    @abstractmethod
    def update(self, feedback: Feedback) -> Feedback:
        """Actualiza un feedback existente"""
        pass
    
    @abstractmethod
    def delete(self, feedback_id: int) -> bool:
        """Elimina un feedback"""
        pass


class AnalysisHistoryRepositoryInterface(ABC):
    """
    Interface para el repositorio de Historial de Análisis.
    """
    
    @abstractmethod
    def save(self, history: AnalysisHistory) -> AnalysisHistory:
        """Guarda un nuevo registro en el historial"""
        pass
    
    @abstractmethod
    def find_by_user_id(
        self, 
        user_id: int,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[AnalysisHistory]:
        """Obtiene el historial de un usuario con paginación"""
        pass
    
    @abstractmethod
    def find_by_id(self, history_id: int) -> Optional[AnalysisHistory]:
        """Busca un registro específico del historial"""
        pass
    
    @abstractmethod
    def filter_by_date_range(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[AnalysisHistory]:
        """Filtra historial por rango de fechas"""
        pass
    
    @abstractmethod
    def filter_by_face_shape(
        self,
        user_id: int,
        face_shape: str
    ) -> List[AnalysisHistory]:
        """Filtra historial por forma de rostro"""
        pass
    
    @abstractmethod
    def filter_by_rating(
        self,
        user_id: int,
        min_rating: int
    ) -> List[AnalysisHistory]:
        """Filtra historial por rating mínimo"""
        pass
    
    @abstractmethod
    def count_by_user_id(self, user_id: int) -> int:
        """Cuenta total de análisis de un usuario"""
        pass
    
    @abstractmethod
    def get_statistics(self, user_id: int) -> dict:
        """Obtiene estadísticas del usuario"""
        pass