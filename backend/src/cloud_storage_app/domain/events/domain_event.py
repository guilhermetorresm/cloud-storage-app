from abc import ABC
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class DomainEvent(ABC):
    """
    Classe base para eventos de domínio.
    Esta classe define a estrutura básica para eventos de domínio, incluindo
    um identificador único, data de criação e tipo de evento.
    """

    event_id: UUID = None
    created_at: datetime = None
    event_type: str = None

    def __post_init__(self):
        if not self.event_id:
            self.event_id = uuid4()
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc)
        if not self.event_type:
            self.event_type = self.__class__.__name__
