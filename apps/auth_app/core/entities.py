# apps/auth_app/domain/entities.py
from dataclasses import dataclass
from shared.core.base_entities import Entity

@dataclass
class User(Entity):
    email: str
    password_hash: str
    is_active: bool = True

@dataclass  
class Profile(Entity):
    user_id: str
    gender: str
    hair_length: str
    preferences: dict