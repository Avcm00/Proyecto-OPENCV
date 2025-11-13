"""
Entidades del dominio de reportes.
Basado en especificación RF-09, RF-10, RF-11
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
@dataclass
class Report:
    user_id: str
    recommendation_id: int
    pdf_url: str
    generated_at: Optional[datetime] = None
    id: Optional[int] = None
    
    def __post_init__(self):
        """Asignar fecha actual si no se proporciona"""
        if self.generated_at is None:
            self.generated_at = datetime.now()