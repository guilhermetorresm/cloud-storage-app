"""
Implementação do serviço JWT para autenticação e autorização.
Responsável por criar, validar e decodificar tokens JWT.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Union
from uuid import uuid4

import jwt
from jwt.exceptions import (
    InvalidTokenError, 
    ExpiredSignatureError, 
    InvalidSignatureError,
    InvalidKeyError,
    InvalidIssuerError,
    InvalidAudienceError
)

from cloud_storage_app.config import get_settings
from cloud_storage_app.domain.value_objects.user_id import UserId


logger = logging.getLogger(__name__)


class TokenPayload:
    """Representa o payload de um token JWT"""
    
    def __init__(
        self,
        sub: str,  # Subject (User ID)
        email: str,
        username: str,
        exp: datetime,
        iat: datetime,
        token_type: str = "access",
        jti: Optional[str] = None,
        iss: Optional[str] = None,
        aud: Optional[str] = None,
        **kwargs
    ):
        self.sub = sub
        self.email = email
        self.username = username
        self.exp = exp
        self.iat = iat
        self.token_type = token_type
        self.jti = jti or str(uuid4())
        self.iss = iss
        self.aud = aud
        self.extra_claims = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o payload para dicionário"""
        payload = {
            "sub": self.sub,
            "email": self.email,
            "username": self.username,
            "exp": int(self.exp.timestamp()),
            "iat": int(self.iat.timestamp()),
            "token_type": self.token_type,
            "jti": self.jti,
        }
        
        if self.iss:
            payload["iss"] = self.iss
        if self.aud:
            payload["aud"] = self.aud
            
        # Adicionar claims extras
        payload.update(self.extra_claims)
        
        return payload
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TokenPayload":
        """Cria TokenPayload a partir de dicionário"""
        # Converter timestamps Unix para datetime
        exp = datetime.fromtimestamp(data["exp"], tz=timezone.utc)
        iat = datetime.fromtimestamp(data["iat"], tz=timezone.utc)
        
        # Extrair claims conhecidos
        known_claims = {
            "sub", "email", "username", "exp", "iat", 
            "token_type", "jti", "iss", "aud"
        }
        extra_claims = {k: v for k, v in data.items() if k not in known_claims}
        
        return cls(
            sub=data["sub"],
            email=data["email"],
            username=data["username"],
            exp=exp,
            iat=iat,
            token_type=data.get("token_type", "access"),
            jti=data.get("jti"),
            iss=data.get("iss"),
            aud=data.get("aud"),
            **extra_claims
        )


class JWTTokens:
    """Representa um par de tokens (access + refresh)"""
    
    def __init__(self, access_token: str, refresh_token: str, token_type: str = "Bearer"):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type
    
    def to_dict(self) -> Dict[str, str]:
        """Converte para dicionário (formato de resposta da API)"""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type
        }


class JWTException(Exception):
    """Exceção base para erros relacionados a JWT"""
    pass


class InvalidTokenException(JWTException):
    """Exceção para tokens inválidos"""
    pass


class ExpiredTokenException(JWTException):
    """Exceção para tokens expirados"""
    pass


class JWTService:
    """Serviço para operações com JWT tokens"""
    
    def __init__(self):
        self._settings = get_settings()
        self._auth_settings = self._settings.auth
        logger.info("JWTService inicializado")
    
    def create_access_token(
        self,
        user_id: Union[str, UserId],
        email: str,
        username: str,
        extra_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Cria um token de acesso JWT.
        
        Args:
            user_id: ID do usuário
            email: Email do usuário
            username: Username do usuário
            extra_claims: Claims adicionais para incluir no token
            
        Returns:
            str: Token JWT codificado
            
        Raises:
            JWTException: Se houver erro na criação do token
        """
        try:
            now = datetime.now(timezone.utc)
            expire = now + self._auth_settings.get_access_token_expire_timedelta()
            
            # Garantir que user_id seja string
            user_id_str = str(user_id) if isinstance(user_id, UserId) else user_id
            
            payload = TokenPayload(
                sub=user_id_str,
                email=email,
                username=username,
                exp=expire,
                iat=now,
                token_type="access",
                iss=self._auth_settings.issuer,
                aud=self._auth_settings.audience,
                **(extra_claims or {})
            )
            
            token = jwt.encode(
                payload.to_dict(),
                self._auth_settings.secret_key,
                algorithm=self._auth_settings.algorithm
            )
            
            logger.debug(f"Access token criado para usuário {user_id_str}")
            return token
            
        except Exception as e:
            logger.error(f"Erro ao criar access token: {str(e)}")
            raise JWTException(f"Falha ao criar access token: {str(e)}") from e
    
    def create_refresh_token(
        self,
        user_id: Union[str, UserId],
        email: str,
        username: str,
        extra_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Cria um token de refresh JWT.
        
        Args:
            user_id: ID do usuário
            email: Email do usuário
            username: Username do usuário
            extra_claims: Claims adicionais para incluir no token
            
        Returns:
            str: Refresh token JWT codificado
            
        Raises:
            JWTException: Se houver erro na criação do token
        """
        try:
            now = datetime.now(timezone.utc)
            expire = now + self._auth_settings.get_refresh_token_expire_timedelta()
            
            # Garantir que user_id seja string
            user_id_str = str(user_id) if isinstance(user_id, UserId) else user_id
            
            payload = TokenPayload(
                sub=user_id_str,
                email=email,
                username=username,
                exp=expire,
                iat=now,
                token_type="refresh",
                iss=self._auth_settings.issuer,
                aud=self._auth_settings.audience,
                **(extra_claims or {})
            )
            
            token = jwt.encode(
                payload.to_dict(),
                self._auth_settings.secret_key,
                algorithm=self._auth_settings.algorithm
            )
            
            logger.debug(f"Refresh token criado para usuário {user_id_str}")
            return token
            
        except Exception as e:
            logger.error(f"Erro ao criar refresh token: {str(e)}")
            raise JWTException(f"Falha ao criar refresh token: {str(e)}") from e
    
    def create_token_pair(
        self,
        user_id: Union[str, UserId],
        email: str,
        username: str,
        extra_claims: Optional[Dict[str, Any]] = None
    ) -> JWTTokens:
        """
        Cria um par de tokens (access + refresh).
        
        Args:
            user_id: ID do usuário
            email: Email do usuário
            username: Username do usuário
            extra_claims: Claims adicionais para incluir nos tokens
            
        Returns:
            JWTTokens: Par de tokens
            
        Raises:
            JWTException: Se houver erro na criação dos tokens
        """
        access_token = self.create_access_token(user_id, email, username, extra_claims)
        refresh_token = self.create_refresh_token(user_id, email, username, extra_claims)
        
        return JWTTokens(access_token=access_token, refresh_token=refresh_token)
    
    def decode_token(self, token: str, verify_expiration: bool = True) -> TokenPayload:
        """
        Decodifica e valida um token JWT.
        
        Args:
            token: Token JWT para decodificar
            verify_expiration: Se deve verificar expiração do token
            
        Returns:
            TokenPayload: Payload decodificado do token
            
        Raises:
            ExpiredTokenException: Se o token estiver expirado
            InvalidTokenException: Se o token for inválido
        """
        try:
            # Configurar opções de verificação
            options = {
                "verify_signature": self._auth_settings.verify_signature,
                "verify_exp": verify_expiration and self._auth_settings.verify_expiration,
                "verify_iat": True,
                "verify_iss": bool(self._auth_settings.issuer),
                "verify_aud": bool(self._auth_settings.audience),
                "require_exp": True,
                "require_iat": True,
            }
            
            # Decodificar token
            payload_dict = jwt.decode(
                token,
                self._auth_settings.secret_key,
                algorithms=[self._auth_settings.algorithm],
                options=options,
                issuer=self._auth_settings.issuer if self._auth_settings.issuer else None,
                audience=self._auth_settings.audience if self._auth_settings.audience else None,
                leeway=timedelta(seconds=self._auth_settings.leeway_seconds)
            )
            
            payload = TokenPayload.from_dict(payload_dict)
            logger.debug(f"Token decodificado com sucesso para usuário {payload.sub}")
            
            return payload
            
        except ExpiredSignatureError as e:
            logger.warning(f"Token expirado: {str(e)}")
            raise ExpiredTokenException("Token expirado") from e
            
        except (InvalidSignatureError, InvalidKeyError) as e:
            logger.error(f"Assinatura do token inválida: {str(e)}")
            raise InvalidTokenException("Assinatura do token inválida") from e
            
        except (InvalidIssuerError, InvalidAudienceError) as e:
            logger.error(f"Issuer ou audience do token inválido: {str(e)}")
            raise InvalidTokenException("Token com origem inválida") from e
            
        except InvalidTokenError as e:
            logger.error(f"Token inválido: {str(e)}")
            raise InvalidTokenException(f"Token inválido: {str(e)}") from e
            
        except Exception as e:
            logger.error(f"Erro inesperado ao decodificar token: {str(e)}")
            raise InvalidTokenException(f"Erro ao processar token: {str(e)}") from e
    
    def validate_token_type(self, payload: TokenPayload, expected_type: str) -> bool:
        """
        Valida se o token é do tipo esperado.
        
        Args:
            payload: Payload do token
            expected_type: Tipo esperado ("access" ou "refresh")
            
        Returns:
            bool: True se o tipo está correto
        """
        return payload.token_type == expected_type
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Cria um novo access token usando um refresh token válido.
        
        Args:
            refresh_token: Refresh token válido
            
        Returns:
            str: Novo access token
            
        Raises:
            InvalidTokenException: Se o refresh token for inválido
            ExpiredTokenException: Se o refresh token estiver expirado
        """
        try:
            # Decodificar e validar refresh token
            payload = self.decode_token(refresh_token)
            
            # Verificar se é um refresh token
            if not self.validate_token_type(payload, "refresh"):
                raise InvalidTokenException("Token fornecido não é um refresh token")
            
            # Criar novo access token
            new_access_token = self.create_access_token(
                user_id=payload.sub,
                email=payload.email,
                username=payload.username,
                extra_claims=payload.extra_claims
            )
            
            logger.debug(f"Access token renovado para usuário {payload.sub}")
            return new_access_token
            
        except (ExpiredTokenException, InvalidTokenException):
            raise  # Re-raise as mesmas exceções
        except Exception as e:
            logger.error(f"Erro ao renovar access token: {str(e)}")
            raise JWTException(f"Falha ao renovar access token: {str(e)}") from e
    
    def get_user_id_from_token(self, token: str) -> str:
        """
        Extrai o ID do usuário de um token válido.
        
        Args:
            token: Token JWT
            
        Returns:
            str: ID do usuário
            
        Raises:
            InvalidTokenException: Se o token for inválido
            ExpiredTokenException: Se o token estiver expirado
        """
        payload = self.decode_token(token)
        return payload.sub
    
    def is_token_expired(self, token: str) -> bool:
        """
        Verifica se um token está expirado sem lançar exceção.
        
        Args:
            token: Token JWT para verificar
            
        Returns:
            bool: True se o token está expirado, False caso contrário
        """
        try:
            self.decode_token(token, verify_expiration=True)
            return False
        except ExpiredTokenException:
            return True
        except InvalidTokenException:
            # Token inválido, mas não necessariamente expirado
            return False
    
    def get_token_expiration(self, token: str) -> datetime:
        """
        Obtém a data de expiração de um token.
        
        Args:
            token: Token JWT
            
        Returns:
            datetime: Data de expiração do token
            
        Raises:
            InvalidTokenException: Se o token for inválido
        """
        payload = self.decode_token(token, verify_expiration=False)
        return payload.exp