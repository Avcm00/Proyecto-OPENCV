from abc import ABC, abstractmethod
from typing import Dict, Any
from ..core.entities import Report


class PDFGeneratorService(ABC):
    
    @abstractmethod
    def generate_report(self, analysis_data: Dict[str, Any], recommendations: Dict[str, Any]) -> str:
        pass