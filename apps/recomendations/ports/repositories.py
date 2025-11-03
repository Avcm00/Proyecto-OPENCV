"""
Interfaces (puertos) para repositorios de persistencia.
"""

from abc import ABC, abstractmethod
from typing import List
from apps.recomendations.core.entities import Recommendation, HaircutStyle, BeardStyle


class RecommendationRepository(ABC):
    @abstractmethod
    def save(self, recommendation: Recommendation):
        pass

    @abstractmethod
    def get_by_user(self, user_id: int) -> List[Recommendation]:
        pass


class StyleRepository(ABC):
    @abstractmethod
    def get_haircuts(self) -> List[HaircutStyle]:
        pass

    @abstractmethod
    def get_beards(self) -> List[BeardStyle]:
        pass
