from dataclasses import dataclass
from datetime import datetime
from .domain_event import DomainEvent
from ..value_objects import UserID

@dataclass
class UserCreated(DomainEvent):
    """Evento de domínio para indicar que um novo usuário foi criado."""
    user_id: UserID
    email: str
    username: str
    created_at: datetime


@dataclass
class UserPasswordChanged(DomainEvent):
    """Evento de domínio para indicar que a senha de um usuário foi alterada."""
    user_id: UserID
    changed_at: datetime


@dataclass
class UserDeactivated(DomainEvent):
    """Evento de domínio para indicar que um usuário foi desativado."""
    user_id: UserID
    deactivated_at: datetime

