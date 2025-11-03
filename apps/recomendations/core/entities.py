"""
Define las entidades principales del dominio de recomendaciones.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
from datetime import datetime


# Enums para tipos de datos
class FaceShape(Enum):
    """Formas de rostro disponibles"""
    OVAL = "oval"
    REDONDO = "redondo"
    CUADRADO = "cuadrado"
    RECTANGULAR = "rectangular"
    CORAZON = "corazon"
    DIAMANTE = "diamante"
    TRIANGULAR = "triangular"


class Gender(Enum):
    """Género del usuario"""
    HOMBRE = "hombre"
    MUJER = "mujer"
    OTRO = "otro"


class HairLength(Enum):
    """Longitud del cabello"""
    CORTO = "corto"
    MEDIO = "medio"
    LARGO = "largo"


class DifficultyLevel(Enum):
    """Nivel de dificultad de mantenimiento"""
    FACIL = "facil"
    MEDIO = "medio"
    DIFICIL = "dificil"


class MaintenanceLevel(Enum):
    """Nivel de mantenimiento requerido"""
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"


# Entidades de dominio
@dataclass
class HaircutStyle:
    """Estilo de corte de cabello"""
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    image_url: str = ""
    suitable_for_shapes: List[FaceShape] = field(default_factory=list)
    suitable_for_gender: List[Gender] = field(default_factory=list)
    hair_length_required: List[HairLength] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    difficulty_level: DifficultyLevel = DifficultyLevel.MEDIO
    popularity_score: float = 0.0
    tags: List[str] = field(default_factory=list)


@dataclass
class BeardStyle:
    """Estilo de barba"""
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    image_url: str = ""
    suitable_for_shapes: List[FaceShape] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    maintenance_level: MaintenanceLevel = MaintenanceLevel.MEDIO
    popularity_score: float = 0.0
    tags: List[str] = field(default_factory=list)


@dataclass
class Recommendation:
    """Recomendación completa de estilos"""
    user_id: int
    face_shape: FaceShape
    gender: Gender
    hair_length: HairLength
    haircut_styles: List[HaircutStyle] = field(default_factory=list)
    beard_styles: List[BeardStyle] = field(default_factory=list)
    confidence_score: float = 0.0
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validaciones después de la inicialización"""
        if not isinstance(self.face_shape, FaceShape):
            if isinstance(self.face_shape, str):
                self.face_shape = FaceShape(self.face_shape.lower())
        
        if not isinstance(self.gender, Gender):
            if isinstance(self.gender, str):
                self.gender = Gender(self.gender.lower())
        
        if not isinstance(self.hair_length, HairLength):
            if isinstance(self.hair_length, str):
                self.hair_length = HairLength(self.hair_length.lower())