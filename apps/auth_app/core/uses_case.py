from abc import ABC, abstractmethod
from .entities import User, Profile

class RegisterUserUseCase:
    def __init__(self, user_repository, password_service):
        self.user_repository = user_repository
        self.password_service = password_service
    
    def execute(self, email: str, password: str) -> User:
        # Lógica de negocio aquí
        hashed_password = self.password_service.hash(password)
        user = User(email=email, password_hash=hashed_password)
        return self.user_repository.save(user)