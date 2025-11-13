"""
Implementación de los repositorios usando Django ORM.
"""

from typing import List, Optional
from apps.recomendations.core.entities import (
    Recommendation, 
    HaircutStyle, 
    BeardStyle,
    FaceShape,
    Gender,
    HairLength,
    DifficultyLevel,
    MaintenanceLevel
)
from ...models import RecommendationModel, HaircutStyleModel, BeardStyleModel

FACE_SHAPE_DB_TO_ENUM = {
    'oval': FaceShape.OVAL,
    'ovalada': FaceShape.OVAL,  # <-- Mapeo para compatibilidad
    'ovalado': FaceShape.OVAL,
    'redonda': FaceShape.REDONDO,
    'redondo': FaceShape.REDONDO,
    'cuadrada': FaceShape.CUADRADO,
    'cuadrado': FaceShape.CUADRADO,
    'corazón': FaceShape.CORAZON,
    'corazon': FaceShape.CORAZON,
    'diamante': FaceShape.DIAMANTE,
    'triangular': FaceShape.TRIANGULAR,
}
GENDER_DB_TO_ENUM = {
    'men': Gender.HOMBRE,
    'male': Gender.HOMBRE,
    'hombre': Gender.HOMBRE,
    'masculino': Gender.HOMBRE,
    'women': Gender.MUJER,
    'female': Gender.MUJER,
    'mujer': Gender.MUJER,
    'femenino': Gender.MUJER,
}

HAIR_LENGTH_DB_TO_ENUM = {
    'corto': HairLength.CORTO,
    'short': HairLength.CORTO,
    'medio': HairLength.MEDIO,
    'medium': HairLength.MEDIO,
    'largo': HairLength.LARGO,
    'long': HairLength.LARGO,
}

class DjangoRecommendationRepository:
    """Repositorio de recomendaciones usando Django ORM"""
    
    def save(self, recommendation: Recommendation) -> Recommendation:
        """
        Guarda una recomendación en la base de datos
        
        Args:
            recommendation: Entidad de recomendación
            
        Returns:
            Recomendación guardada con ID asignado
        """
        # Convertir enums a strings para guardar
        model = RecommendationModel(
            user_id=recommendation.user_id,
            face_shape=recommendation.face_shape.value,
            gender=recommendation.gender.value,
            hair_length=recommendation.hair_length.value,
            confidence_score=recommendation.confidence_score,
            haircut_styles_ids=[style.id for style in recommendation.haircut_styles if style.id],
            beard_styles_ids=[style.id for style in recommendation.beard_styles if style.id],
        )
        model.save()
        
        # Actualizar el ID en la entidad
        recommendation.id = model.id
        recommendation.created_at = model.created_at
        
        return recommendation

    def get_by_user(self, user_id: int, limit: int = 100) -> List[Recommendation]:
        """
        Obtiene las recomendaciones de un usuario
        
        Args:
            user_id: ID del usuario
            limit: Número máximo de resultados
            
        Returns:
            Lista de recomendaciones
        """
        models = RecommendationModel.objects.filter(
            user_id=user_id
        ).order_by('-created_at')[:limit]
        
        recommendations = []
        for model in models:
            # Convertir el modelo Django a entidad de dominio
            recommendation = Recommendation(
                id=model.id,
                user_id=model.user_id,
                face_shape=FaceShape(model.face_shape),
                gender=Gender(model.gender),
                hair_length=HairLength(model.hair_length),
                confidence_score=model.confidence_score,
                haircut_styles=[],  # Se cargarían por separado si es necesario
                beard_styles=[],
                created_at=model.created_at
            )
            recommendations.append(recommendation)
        
        return recommendations

    def get_by_id(self, recommendation_id: int) -> Optional[Recommendation]:
        """
        Obtiene una recomendación por ID
        
        Args:
            recommendation_id: ID de la recomendación
            
        Returns:
            Recomendación o None si no existe
        """
        try:
            model = RecommendationModel.objects.get(id=recommendation_id)
            return Recommendation(
                id=model.id,
                user_id=model.user_id,
                face_shape=FaceShape(model.face_shape),
                gender=Gender(model.gender),
                hair_length=HairLength(model.hair_length),
                confidence_score=model.confidence_score,
                haircut_styles=[],
                beard_styles=[],
                created_at=model.created_at
            )
        except RecommendationModel.DoesNotExist:
            return None


class DjangoStyleRepository:
    """Repositorio de estilos usando Django ORM"""
    
    
    def get_haircuts(
        self,
        gender: Gender = None,
        hair_length: HairLength = None,
        face_shape: FaceShape = None
    ) -> List[HaircutStyle]:
        """
        Obtiene estilos de corte con filtros opcionales
        """
        from apps.recomendations.models import HaircutStyleModel

        queryset = HaircutStyleModel.objects.filter(is_active=True)

        # 🔧 Filtro de género corregido
        if gender:
            # Mapear enum a valor de BD
            gender_db_values = {
                Gender.HOMBRE: ['men', 'male', 'hombre'],
                Gender.MUJER: ['women', 'female', 'mujer']
            }
            db_values = gender_db_values.get(gender, [])
            if db_values:
                queryset = queryset.filter(gender__in=db_values)

        # 🔧 NO filtrar por face_shape o hair_length aquí
        # Esos filtros se aplican después de convertir a entidades
        # porque la BD usa strings y las entidades usan enums

        # Convertir a entidades
        all_styles = [self._haircut_model_to_entity(model) for model in queryset]

        # 🔧 Aplicar filtros de face_shape y hair_length DESPUÉS de conversión
        filtered_styles = all_styles

        if face_shape:
            filtered_styles = [
                style for style in filtered_styles 
                if face_shape in style.suitable_for_shapes
            ]

        if hair_length:
            filtered_styles = [
                style for style in filtered_styles 
                if hair_length in style.hair_length_required
            ]

        return filtered_styles

    def get_beards(
        self,
        gender: Optional[Gender] = None,
        face_shape: Optional[FaceShape] = None
    ) -> List[BeardStyle]:
        """
        Obtiene estilos de barba con filtros opcionales
        
        Args:
            gender: Filtrar por género
            face_shape: Filtrar por forma de rostro
            
        Returns:
            Lista de estilos de barba
        """
        queryset = BeardStyleModel.objects.all()
        
        # Aplicar filtros
        if face_shape:
            queryset = queryset.filter(suitable_for_shapes__contains=face_shape.value)
        
        # Convertir modelos Django a entidades de dominio
        return [self._beard_model_to_entity(model) for model in queryset]

    def get_haircut_by_id(self, style_id: int) -> Optional[HaircutStyle]:
        """Obtiene un estilo de corte por ID"""
        try:
            model = HaircutStyleModel.objects.get(id=style_id)
            return self._haircut_model_to_entity(model)
        except HaircutStyleModel.DoesNotExist:
            return None

    def get_beard_by_id(self, style_id: int) -> Optional[BeardStyle]:
        """Obtiene un estilo de barba por ID"""
        try:
            model = BeardStyleModel.objects.get(id=style_id)
            return self._beard_model_to_entity(model)
        except BeardStyleModel.DoesNotExist:
            return None

    def _haircut_model_to_entity(self, model):
        """
        Convierte un modelo Django de corte a entidad de dominio.
        Incluye normalización de valores de BD a enums.
        """
        from apps.recomendations.core.entities import (
            HaircutStyle, FaceShape, Gender, HairLength
        )

        # Normalizar suitable_for_shapes
        suitable_shapes = []
        for shape in model.suitable_for_shapes:
            normalized_shape = shape.lower().strip()
            if normalized_shape in FACE_SHAPE_DB_TO_ENUM:
                suitable_shapes.append(FACE_SHAPE_DB_TO_ENUM[normalized_shape])
            else:
                print(f"⚠️ WARNING: Shape '{shape}' no reconocida, ignorando...")

        # Normalizar suitable_for_gender
        suitable_genders = []
        for gender in model.suitable_for_gender:
            normalized_gender = gender.lower().strip()
            if normalized_gender in GENDER_DB_TO_ENUM:
                suitable_genders.append(GENDER_DB_TO_ENUM[normalized_gender])
            else:
                print(f"⚠️ WARNING: Gender '{gender}' no reconocido, ignorando...")

        # Normalizar hair_length_required
        hair_lengths = []
        for length in model.hair_length_required:
            normalized_length = length.lower().strip()
            if normalized_length in HAIR_LENGTH_DB_TO_ENUM:
                hair_lengths.append(HAIR_LENGTH_DB_TO_ENUM[normalized_length])
            else:
                print(f"⚠️ WARNING: Hair length '{length}' no reconocido, ignorando...")

        return HaircutStyle(
            id=model.id,
            name=model.name,
            description=model.description,
            image_url=model.image_url,
            suitable_for_shapes=suitable_shapes,
            suitable_for_gender=suitable_genders,
            hair_length_required=hair_lengths,
            benefits=model.benefits,
            tags=model.tags,
            difficulty_level=model.difficulty_level,
            popularity_score=model.popularity_score
        )

    
    def _beard_model_to_entity(self, model):
        """
        Convierte un modelo Django de barba a entidad de dominio.
        SIN maintenance_level porque no existe en el modelo de BD.
        """
        from apps.recomendations.core.entities import BeardStyle, FaceShape

        # Normalizar suitable_for_shapes
        suitable_shapes = []
        for shape in model.suitable_for_shapes:
            normalized_shape = shape.lower().strip()
            if normalized_shape in FACE_SHAPE_DB_TO_ENUM:
                suitable_shapes.append(FACE_SHAPE_DB_TO_ENUM[normalized_shape])
            else:
                print(f"⚠️ WARNING: Shape '{shape}' no reconocida en barba, ignorando...")

        # ✅ Crear BeardStyle SIN maintenance_level
        return BeardStyle(
            id=model.id,
            name=model.name,
            description=model.description,
            image_url=model.image_url,
            suitable_for_shapes=suitable_shapes,
            benefits=model.benefits if model.benefits else [],
            popularity_score=model.popularity_score if model.popularity_score else 0.0,
            tags=model.tags if model.tags else []
        )


# Mantener las clases SQL para compatibilidad (si las necesitas)
class SQLRecommendationRepository:
    """Repositorio usando SQLAlchemy (legacy)"""
    def __init__(self, db_session):
        self.db = db_session

    def save(self, recommendation: Recommendation):
        model = RecommendationModel(
            user_id=recommendation.user_id,
            face_shape=recommendation.face_shape.value,
            gender=recommendation.gender.value,
            hair_length=recommendation.hair_length.value,
            confidence_score=recommendation.confidence_score,
        )
        self.db.add(model)
        self.db.commit()
        return model

    def get_by_user(self, user_id: int):
        return self.db.query(RecommendationModel).filter_by(user_id=user_id).all()


class SQLStyleRepository:
    """Repositorio de estilos usando SQLAlchemy (legacy)"""
    def __init__(self, db_session):
        self.db = db_session

    def get_haircuts(self):
        rows = self.db.query(HaircutStyleModel).all()
        return [
            HaircutStyle(
                id=r.id,
                name=r.name,
                description=r.description,
                image_url=r.image_url,
                suitable_for_shapes=[FaceShape(s) for s in r.suitable_shapes]
            ) 
            for r in rows
        ]

    def get_beards(self):
        rows = self.db.query(BeardStyleModel).all()
        return [
            BeardStyle(
                id=r.id,
                name=r.name,
                description=r.description,
                image_url=r.image_url,
                suitable_for_shapes=[FaceShape(s) for s in r.suitable_shapes]
            ) 
            for r in rows
        ]