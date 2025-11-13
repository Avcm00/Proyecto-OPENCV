"""
Entidades del dominio de Feedback.
Representan los conceptos del negocio relacionados con feedback e historial.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Feedback:
    """
    Representa el feedback de un usuario sobre un análisis.
    """
    user_id: int
    analysis_id: int
    rating: int  # 1-5 estrellas
    liked: Optional[bool] = None  # True=like, False=dislike, None=sin calificar
    comment: Optional[str] = None
    created_at: Optional[datetime] = None
    id: Optional[int] = None


    """Entidad que representa un feedback de usuario."""
    id: int
    analysis_id: int
    user_id: int
    rating: int
    liked: Optional[bool]
    comment: Optional[str]
    created_at: datetime
    
    def get_formatted_date(self) -> str:
        """Retorna la fecha formateada."""
        return self.created_at.strftime('%d de %B de %Y a las %H:%M')
    
    def __post_init__(self):
        # Validar rating
        if not 1 <= self.rating <= 5:
            raise ValueError("Rating debe estar entre 1 y 5")
        
        # Validar comentario (máximo 500 caracteres)
        if self.comment and len(self.comment) > 500:
            raise ValueError("Comentario no puede exceder 500 caracteres")
    
    def is_positive(self) -> bool:
        """Retorna True si el feedback es positivo (rating >= 4)"""
        return self.rating >= 4
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la entidad a diccionario"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'analysis_id': self.analysis_id,
            'rating': self.rating,
            'liked': self.liked,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class AnalysisHistory:
    """
    Representa un registro en el historial de análisis de un usuario.
    """
    user_id: int
    face_shape: str
    confidence: float
    recommendations_count: int
    pdf_path: Optional[str] = None
    feedback_rating: Optional[int] = None
    created_at: Optional[datetime] = None
    id: Optional[int] = None
    
    # Datos completos del análisis (para vista detallada)
    analysis_data: Optional[Dict[str, Any]] = None
    recommendations_data: Optional[Dict[str, Any]] = None
    
    def has_feedback(self) -> bool:
        """Retorna True si el análisis tiene feedback"""
        return self.feedback_rating is not None
    
    def get_confidence_percentage(self) -> str:
        """Retorna la confianza formateada como porcentaje"""
        return f"{self.confidence:.1f}%"
    
    def get_formatted_date(self) -> str:
        """Retorna la fecha formateada"""
        if self.created_at:
            return self.created_at.strftime("%d/%m/%Y %H:%M")
        return "N/A"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la entidad a diccionario"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'face_shape': self.face_shape,
            'confidence': self.confidence,
            'recommendations_count': self.recommendations_count,
            'pdf_path': self.pdf_path,
            'feedback_rating': self.feedback_rating,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'has_feedback': self.has_feedback(),
            'formatted_date': self.get_formatted_date()
        }