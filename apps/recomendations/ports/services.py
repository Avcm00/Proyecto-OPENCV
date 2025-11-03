"""
Interfaces (puertos) de servicios externos.
"""

from abc import ABC, abstractmethod


class RecommendationEngine(ABC):
    @abstractmethod
    def generate_recommendations(self, user_profile, styles):
        pass


class StyleCatalogService(ABC):
    @abstractmethod
    def get_haircuts(self):
        pass

    @abstractmethod
    def get_beards(self):
        pass
