from dataclasses import dataclass
from datetime import datetime
from .domain_event import DomainEvent
from ..value_objects import UserId

@dataclass
class UserCreated(DomainEvent):
    """Evento de domínio para indicar que um novo usuário foi criado."""
    user_id: UserId = None
    email: str = None
    username: str = None
    created_at: datetime = None


@dataclass
class UserPasswordChanged(DomainEvent):
    """Evento de domínio para indicar que a senha de um usuário foi alterada."""
    user_id: UserId = None
    changed_at: datetime = None


@dataclass
class UserDeactivated(DomainEvent):
    """Evento de domínio para indicar que um usuário foi desativado."""
    user_id: UserId = None
    deactivated_at: datetime = None

