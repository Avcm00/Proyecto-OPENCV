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

    def get_by_user(self, user_id: int, limit: int = 10) -> List[Recommendation]:
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
        gender: Optional[Gender] = None,
        hair_length: Optional[HairLength] = None,
        face_shape: Optional[FaceShape] = None
    ) -> List[HaircutStyle]:
        """
        Obtiene estilos de corte de cabello con filtros opcionales
        
        Args:
            gender: Filtrar por género
            hair_length: Filtrar por longitud de cabello
            face_shape: Filtrar por forma de rostro
            
        Returns:
            Lista de estilos de corte
        """
        queryset = HaircutStyleModel.objects.all()
        
        # Aplicar filtros si se proporcionan
        if gender:
            queryset = queryset.filter(suitable_for_gender__contains=gender.value)
        
        if hair_length:
            queryset = queryset.filter(hair_length_required__contains=hair_length.value)
        
        if face_shape:
            queryset = queryset.filter(suitable_for_shapes__contains=face_shape.value)
        
        # Convertir modelos Django a entidades de dominio
        return [self._haircut_model_to_entity(model) for model in queryset]

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

    def _haircut_model_to_entity(self, model: HaircutStyleModel) -> HaircutStyle:
        """Convierte un modelo Django a entidad de dominio"""
        return HaircutStyle(
            id=model.id,
            name=model.name,
            description=model.description,
            image_url=model.image_url,
            suitable_for_shapes=[
                FaceShape(shape) for shape in model.suitable_for_shapes
            ] if model.suitable_for_shapes else [],
            suitable_for_gender=[
                Gender(gender) for gender in model.suitable_for_gender
            ] if hasattr(model, 'suitable_for_gender') and model.suitable_for_gender else [],
            hair_length_required=[
                HairLength(length) for length in model.hair_length_required
            ] if hasattr(model, 'hair_length_required') and model.hair_length_required else [],
            benefits=model.benefits if hasattr(model, 'benefits') else [],
            difficulty_level=DifficultyLevel(model.difficulty_level) if hasattr(model, 'difficulty_level') and model.difficulty_level else DifficultyLevel.MEDIO,
            popularity_score=model.popularity_score if hasattr(model, 'popularity_score') else 0.0,
            tags=model.tags if hasattr(model, 'tags') else []
        )

    def _beard_model_to_entity(self, model: BeardStyleModel) -> BeardStyle:
        """Convierte un modelo Django a entidad de dominio"""
        return BeardStyle(
            id=model.id,
            name=model.name,
            description=model.description,
            image_url=model.image_url,
            suitable_for_shapes=[
                FaceShape(shape) for shape in model.suitable_for_shapes
            ] if model.suitable_for_shapes else [],
            benefits=model.benefits if hasattr(model, 'benefits') else [],
            maintenance_level=MaintenanceLevel(model.maintenance_level) if hasattr(model, 'maintenance_level') and model.maintenance_level else MaintenanceLevel.MEDIO,
            popularity_score=model.popularity_score if hasattr(model, 'popularity_score') else 0.0,
            tags=model.tags if hasattr(model, 'tags') else []
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