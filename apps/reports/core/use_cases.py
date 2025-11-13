"""
Casos de uso del módulo de reportes.
Implementa lógica de negocio según especificación RF-09.
"""

from typing import Dict, Any
from .entities import Report
from ..ports.services import PDFGeneratorService


class GeneratePDFReportUseCase:
    """
    Caso de uso para generar reportes PDF del análisis facial.
    
    Según especificación:
    - Recibe datos del análisis y recomendaciones
    - Genera PDF usando el servicio
    - Retorna entidad Report con la ruta del PDF
    """
    
    def __init__(self, pdf_generator: PDFGeneratorService):
        """
        Args:
            pdf_generator: Servicio que genera el PDF
        """
        self.pdf_generator = pdf_generator
    
    def execute(
        self, 
        user_id: str,
        recommendation_id: int,
        analysis_data: Dict[str, Any],
        recommendations: Dict[str, Any]
    ) -> Report:
        """
        Ejecuta la generación del reporte PDF.
        
        Args:
            user_id: ID del usuario
            recommendation_id: ID de la recomendación
            analysis_data: Datos del análisis facial
            recommendations: Recomendaciones generadas
        
        Returns:
            Report: Entidad con la ruta del PDF generado
        """
        # Generar el PDF usando el servicio
        pdf_path = self.pdf_generator.generate_report(
            analysis_data=analysis_data,
            recommendations=recommendations
        )
        
        # Crear y retornar la entidad Report
        report = Report(
            user_id=user_id,
            recommendation_id=recommendation_id,
            pdf_url=pdf_path
        )
        
        return report