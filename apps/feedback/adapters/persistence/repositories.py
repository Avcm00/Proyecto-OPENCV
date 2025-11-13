"""
Implementación de los repositorios usando Django ORM.
"""
from typing import List, Optional, Union
import uuid

from datetime import datetime

from ...core.entities import Feedback, AnalysisHistory
from ...ports.repositories import (
    FeedbackRepositoryInterface,
    AnalysisHistoryRepositoryInterface
)
from .models import FeedbackModel, AnalysisHistoryModel


class DjangoFeedbackRepository(FeedbackRepositoryInterface):
    """
    Repositorio de Feedback usando Django ORM.
    """
    
    def _to_entity(self, model: FeedbackModel) -> Feedback:
        """Convierte modelo Django a entidad de dominio"""
        return Feedback(
            id=model.id,
            user_id=model.user_id,
            analysis_id=model.analysis_history_id,
            rating=model.rating,
            liked=model.liked,
            comment=model.comment,
            created_at=model.created_at
        )
    
    def save(self, feedback: Feedback) -> Feedback:
        """Guarda un nuevo feedback"""
        model = FeedbackModel.objects.create(
            user_id=feedback.user_id,
            analysis_history_id=feedback.analysis_id,
            rating=feedback.rating,
            liked=feedback.liked,
            comment=feedback.comment,
            created_at=feedback.created_at
        )
        return self._to_entity(model)
    
    def find_by_analysis_id(self, analysis_id: int) -> Optional[Feedback]:
        """Busca feedback por ID de análisis"""
        try:
            model = FeedbackModel.objects.get(analysis_history_id=analysis_id)
            return self._to_entity(model)
        except FeedbackModel.DoesNotExist:
            return None
    
    def find_by_user_id(
        self,
        user_id: Union[uuid.UUID, str],
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Feedback]:
        queryset = FeedbackModel.objects.filter(user_id=user_id)
        if offset:
            queryset = queryset[offset:]
        if limit:
            queryset = queryset[:limit]
        return [self._to_entity(m) for m in queryset]
    
    def count_by_user_id(self, user_id: Union[uuid.UUID, str]) -> int:
        return FeedbackModel.objects.filter(user_id=user_id).count()
    
    def update(self, feedback: Feedback) -> Feedback:
        """Actualiza un feedback existente"""
        model = FeedbackModel.objects.get(id=feedback.id)
        model.rating = feedback.rating
        model.liked = feedback.liked
        model.comment = feedback.comment
        model.save()
        return self._to_entity(model)
    
    def delete(self, feedback_id: int) -> bool:
        """Elimina un feedback"""
        try:
            FeedbackModel.objects.get(id=feedback_id).delete()
            return True
        except FeedbackModel.DoesNotExist:
            return False


class DjangoAnalysisHistoryRepository(AnalysisHistoryRepositoryInterface):
    """
    Repositorio de Historial de Análisis usando Django ORM.
    """
    
    def _to_entity(self, model: AnalysisHistoryModel) -> AnalysisHistory:
        """Convierte modelo Django a entidad de dominio"""
        return AnalysisHistory(
            id=model.id,
            user_id=model.user_id,
            face_shape=model.face_shape,
            confidence=model.confidence,
            recommendations_count=model.recommendations_count,
            pdf_path=model.pdf_path,
            feedback_rating=model.feedback_rating,
            created_at=model.created_at,
            analysis_data=model.analysis_data,
            recommendations_data=model.recommendations_data
        )
    
    def save(self, history: AnalysisHistory) -> AnalysisHistory:
        """Guarda un nuevo registro en el historial"""
        model = AnalysisHistoryModel.objects.create(
            user_id=history.user_id,
            face_shape=history.face_shape,
            confidence=history.confidence,
            recommendations_count=history.recommendations_count,
            pdf_path=history.pdf_path,
            analysis_data=history.analysis_data,
            recommendations_data=history.recommendations_data
        )
        return self._to_entity(model)
    
    def find_by_user_id(
        self,
        user_id: int,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[AnalysisHistory]:
        """Obtiene el historial de un usuario con paginación"""
        queryset = AnalysisHistoryModel.objects.filter(user_id=user_id)
        
        if offset:
            queryset = queryset[offset:]
        if limit:
            queryset = queryset[:limit]
        
        return [self._to_entity(m) for m in queryset]
    
    def find_by_id(self, history_id: int) -> Optional[AnalysisHistory]:
        """Busca un registro específico del historial"""
        try:
            model = AnalysisHistoryModel.objects.get(id=history_id)
            return self._to_entity(model)
        except AnalysisHistoryModel.DoesNotExist:
            return None
    
    def filter_by_date_range(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[AnalysisHistory]:
        """Filtra historial por rango de fechas"""
        models = AnalysisHistoryModel.objects.filter(
            user_id=user_id,
            created_at__range=[start_date, end_date]
        )
        return [self._to_entity(m) for m in models]
    
    def filter_by_face_shape(
        self,
        user_id: int,
        face_shape: str
    ) -> List[AnalysisHistory]:
        """Filtra historial por forma de rostro"""
        models = AnalysisHistoryModel.objects.filter(
            user_id=user_id,
            face_shape=face_shape
        )
        return [self._to_entity(m) for m in models]
    
    def filter_by_rating(
        self,
        user_id: int,
        min_rating: int
    ) -> List[AnalysisHistory]:
        """Filtra historial por rating mínimo"""
        models = AnalysisHistoryModel.objects.filter(
            user_id=user_id,
            feedbacks__rating__gte=min_rating
        )
        return [self._to_entity(m) for m in models]
    
    def count_by_user_id(self, user_id: int) -> int:
        """Cuenta total de análisis de un usuario"""
        return AnalysisHistoryModel.objects.filter(user_id=user_id).count()
    
    def get_statistics(self, user_id: int) -> dict:
        """Obtiene estadísticas del historial de un usuario."""
        from django.db.models import Count, Avg
        
        total_analyses = AnalysisHistoryModel.objects.filter(user_id=user_id).count()
        
        # Promedio de calificaciones (usando 'feedbacks' plural)
        avg_rating = AnalysisHistoryModel.objects.filter(
            user_id=user_id,
            feedbacks__isnull=False
        ).aggregate(
            avg=Avg('feedbacks__rating')
        )['avg'] or 0
        
        # Forma más detectada
        most_common_shape = AnalysisHistoryModel.objects.filter(
            user_id=user_id
        ).values('face_shape').annotate(
            count=Count('id')
        ).order_by('-count').first()
        
        # Total de feedbacks dados
        total_feedbacks = FeedbackModel.objects.filter(user_id=user_id).count()
        
        return {
            'total_analyses': total_analyses,
            'average_rating': round(avg_rating, 1) if avg_rating else 0,
            'most_common_shape': most_common_shape['face_shape'] if most_common_shape else 'N/A',
            'total_feedbacks': total_feedbacks
        }