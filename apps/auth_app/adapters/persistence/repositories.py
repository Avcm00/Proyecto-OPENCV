from typing import Optional
from ...ports.repositories import UserRepository
from ...core.entities import User
from .models import UserModel

class DjangoUserRepository(UserRepository):
    def save(self, user: User) -> User:
        user_model = UserModel.objects.create(
            email=user.email,
            password_hash=user.password_hash
        )
        return User(id=user_model.id, email=user_model.email, password_hash=user_model.password_hash)
    
    def find_by_email(self, email: str) -> Optional[User]:
        try:
            user_model = UserModel.objects.get(email=email)
            return User(id=user_model.id, email=user_model.email, password_hash=user_model.password_hash)
        except UserModel.DoesNotExist:
            return None