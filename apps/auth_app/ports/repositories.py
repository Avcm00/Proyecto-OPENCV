from abc import ABC, abstractmethod
from typing import Optional
from ..core.entities import User

class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> User:
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass