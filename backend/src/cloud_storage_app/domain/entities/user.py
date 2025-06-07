from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Optional, List
from ..value_objects import (
    UserId, Email, Username, HashedPassword, ProfilePicture, UserDescription, FirstName, LastName
)
from ..events.domain_event import DomainEvent
from ..events.user_domain_events import (
    UserCreated, UserPasswordChanged, UserDeactivated
)

@dataclass
class User:
    """
    Entidade User representando um usuário do sistema de cloud storage.
    
    Esta entidade segue os princípios do DDD, encapsulando as regras de negócio
    relacionadas ao usuário e mantendo sua consistência através de invariantes.
    """

    # Identificador único do usuário
    _user_id: UserId
    _username: Username
    _email: Email
    
    # Dados de autenticação
    _hashed_password: HashedPassword

    # Dados do usuário
    _first_name: FirstName
    _last_name: Optional[LastName] = None
    _profile_picture: Optional[ProfilePicture] = None
    _description: Optional[UserDescription] = None

    # Controle de estado
    _is_active: bool = True

    # Timestamps
    _created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _last_login_at: Optional[datetime] = None

    _domain_events: List[DomainEvent] = field(default_factory=list)


    def __post_init__(self):
        """Método de inicialização para validações"""
        if not self._username:
            raise ValueError("Nome de usuário é obrigatório")
        if not self._first_name:
            raise ValueError("Primeiro nome é obrigatório")
        if not self._email:
            raise ValueError("Email é obrigatório")
        if not self._hashed_password:
            raise ValueError("Senha é obrigatória")

    @classmethod
    def create(cls, username: str, email: str, hashed_password: str, 
                   first_name: str, last_name: str, profile_picture: str = None, description: str = None) -> "User":
        """Cria um novo usuário com os dados fornecidos.
        
        Args:
            username: Nome de usuário
            email: Email do usuário
            hashed_password: Senha já hasheada
            first_name: Primeiro nome do usuário
            last_name: Último nome do usuário (opcional)
            profile_picture: URL da foto de perfil (opcional)
            description: Descrição do usuário (opcional)
            
        Returns:
            User: Nova instância de usuário
            
        Raises:
            ValueError: Se os dados fornecidos forem inválidos
        """
        # Cria a instância do usuário
        user = cls(
            _user_id=UserId.generate(),
            _username=Username(username),
            _email=Email(email),
            _hashed_password=HashedPassword(hashed_password),
            _first_name=FirstName(first_name),
            _last_name=LastName(last_name) if last_name else None,
            _profile_picture=ProfilePicture(profile_picture) if profile_picture else None,
            _description=UserDescription(description) if description else None
        )
        
        # Adiciona o evento de domínio
        user._add_domain_event(UserCreated(user.user_id, user.email, user.username, user.created_at))
        
        return user

    # Getters
    @property
    def user_id(self) -> UserId:
        return self._user_id

    @property
    def username(self) -> Username:
        return self._username

    @property
    def email(self) -> Email:
        return self._email
    
    @property
    def first_name(self) -> FirstName:
        return self._first_name
    
    @property
    def last_name(self) -> Optional[LastName]:
        return self._last_name if self._last_name else None
    
    @property
    def hashed_password(self) -> HashedPassword:
        return self._hashed_password

    @property
    def full_name(self) -> str:
        return f"{self._first_name} {self._last_name}" if self._last_name else self._first_name

    @property
    def profile_picture(self) -> ProfilePicture:
        return self._profile_picture

    @property
    def description(self) -> UserDescription:
        return self._description

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def last_login_at(self) -> Optional[datetime]:
        return self._last_login_at

    # Métodos de domínio
    def update_profile(self, first_name: Optional[str] = None,
                      last_name: Optional[str] = None,
                      profile_picture: Optional[str] = None,
                      description: Optional[str] = None) -> None:
        """Atualiza os dados do perfil do usuário."""
        if first_name:
            self._first_name = FirstName(first_name)
        if last_name:
            self._last_name = last_name
        if profile_picture:
            self._profile_picture = profile_picture
        if description:
            self._description = description
        
        self._mark_as_updated()

    def change_password(self, new_hashed_password: HashedPassword) -> None:
        """Altera a senha do usuário."""
        self._hashed_password = new_hashed_password
        self._mark_as_updated()
        self._add_domain_event(UserPasswordChanged(self._user_id, self._updated_at))

    def deactivate(self) -> None:
        """Desativa o usuário."""
        if not self._is_active:
            raise ValueError("Usuário já está desativado")
        
        self._is_active = False
        self._updated_at = datetime.now(UTC)
        self._add_domain_event(UserDeactivated(self._user_id, self._updated_at))

    def activate(self) -> None:
        """Reativa o usuário."""
        if self._is_active:
            raise ValueError("Usuário já está ativo")
        
        self._is_active = True
        self._mark_as_updated()

    def update_last_login(self) -> None:
        """Atualiza o timestamp do último login."""
        self._last_login_at = datetime.now(UTC)

    def _mark_as_updated(self) -> None:
        """Marca o usuário como atualizado."""
        self._updated_at = datetime.now(UTC)
        
    def _add_domain_event(self, event: DomainEvent) -> None:
        """Adiciona um evento de domínio."""
        self._domain_events.append(event)

    def clear_domain_events(self) -> None:
        """Limpa os eventos de domínio (usado após publicação)."""
        self._domain_events.clear()
