"""
Teste básico para o JWTService
Execute com: python -m pytest test_jwt_service.py -v
"""

import pytest
import os
from uuid import UUID
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

# Configurar variáveis de ambiente antes de importar
os.environ.update({
    "SECRET_KEY": "test_secret_key_with_at_least_32_characters_for_security",
    "JWT_ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "15",
    "REFRESH_TOKEN_EXPIRE_DAYS": "7",
    "JWT_ISSUER": "test-api",
    "JWT_AUDIENCE": "test-users"
})

from cloud_storage_app.infrastructure.auth.jwt_service import (
    JWTService, 
    TokenPayload, 
    JWTTokens,
    InvalidTokenException,
    ExpiredTokenException
)
from cloud_storage_app.domain.value_objects.user_id import UserId


class TestJWTService:
    """Testes básicos para o JWTService"""
    
    @pytest.fixture
    def jwt_service(self):
        """Fixture que retorna uma instância do JWTService"""
        return JWTService()
    
    @pytest.fixture
    def user_data(self):
        """Fixture com dados de usuário para teste"""
        return {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "teste@email.com",
            "username": "usuario_teste"
        }
    
    def test_create_access_token(self, jwt_service, user_data):
        """Teste básico de criação de access token"""
        token = jwt_service.create_access_token(
            user_id=user_data["user_id"],
            email=user_data["email"],
            username=user_data["username"]
        )
        
        assert isinstance(token, str)
        assert len(token) > 0
        assert token.count('.') == 2  # JWT tem 3 partes separadas por ponto
    
    def test_create_refresh_token(self, jwt_service, user_data):
        """Teste básico de criação de refresh token"""
        token = jwt_service.create_refresh_token(
            user_id=user_data["user_id"],
            email=user_data["email"],
            username=user_data["username"]
        )
        
        assert isinstance(token, str)
        assert len(token) > 0
        assert token.count('.') == 2
    
    def test_create_token_pair(self, jwt_service, user_data):
        """Teste de criação de par de tokens"""
        tokens = jwt_service.create_token_pair(
            user_id=user_data["user_id"],
            email=user_data["email"],
            username=user_data["username"]
        )
        
        assert isinstance(tokens, JWTTokens)
        assert isinstance(tokens.access_token, str)
        assert isinstance(tokens.refresh_token, str)
        assert tokens.token_type == "Bearer"
        
        # Verificar se os tokens são diferentes
        assert tokens.access_token != tokens.refresh_token
    
    def test_decode_valid_token(self, jwt_service, user_data):
        """Teste de decodificação de token válido"""
        # Criar token
        token = jwt_service.create_access_token(
            user_id=user_data["user_id"],
            email=user_data["email"],
            username=user_data["username"]
        )
        
        # Decodificar token
        payload = jwt_service.decode_token(token)
        
        assert isinstance(payload, TokenPayload)
        assert payload.sub == user_data["user_id"]
        assert payload.email == user_data["email"]
        assert payload.username == user_data["username"]
        assert payload.token_type == "access"
    
    def test_decode_invalid_token(self, jwt_service):
        """Teste de decodificação de token inválido"""
        invalid_token = "token.invalido.aqui"
        
        with pytest.raises(InvalidTokenException):
            jwt_service.decode_token(invalid_token)
    
    def test_token_types(self, jwt_service, user_data):
        """Teste para verificar tipos de token"""
        access_token = jwt_service.create_access_token(
            user_id=user_data["user_id"],
            email=user_data["email"],
            username=user_data["username"]
        )
        
        refresh_token = jwt_service.create_refresh_token(
            user_id=user_data["user_id"],
            email=user_data["email"],
            username=user_data["username"]
        )
        
        access_payload = jwt_service.decode_token(access_token)
        refresh_payload = jwt_service.decode_token(refresh_token)
        
        assert access_payload.token_type == "access"
        assert refresh_payload.token_type == "refresh"
        
        # Validar tipos
        assert jwt_service.validate_token_type(access_payload, "access")
        assert jwt_service.validate_token_type(refresh_payload, "refresh")
        assert not jwt_service.validate_token_type(access_payload, "refresh")
    
    def test_get_user_id_from_token(self, jwt_service, user_data):
        """Teste de extração de user_id do token"""
        token = jwt_service.create_access_token(
            user_id=user_data["user_id"],
            email=user_data["email"],
            username=user_data["username"]
        )
        
        extracted_user_id = jwt_service.get_user_id_from_token(token)
        assert extracted_user_id == user_data["user_id"]
    
    def test_refresh_access_token(self, jwt_service, user_data):
        """Teste de renovação de access token"""
        # Criar refresh token
        refresh_token = jwt_service.create_refresh_token(
            user_id=user_data["user_id"],
            email=user_data["email"],
            username=user_data["username"]
        )
        
        # Renovar access token
        new_access_token = jwt_service.refresh_access_token(refresh_token)
        
        assert isinstance(new_access_token, str)
        assert len(new_access_token) > 0
        
        # Verificar se o novo token é válido
        payload = jwt_service.decode_token(new_access_token)
        assert payload.sub == user_data["user_id"]
        assert payload.token_type == "access"
    
    def test_refresh_with_access_token_should_fail(self, jwt_service, user_data):
        """Teste que verifica falha ao tentar renovar com access token"""
        # Criar access token
        access_token = jwt_service.create_access_token(
            user_id=user_data["user_id"],
            email=user_data["email"],
            username=user_data["username"]
        )
        
        # Tentar renovar com access token (deve falhar)
        with pytest.raises(InvalidTokenException, match="não é um refresh token"):
            jwt_service.refresh_access_token(access_token)
    
    def test_token_with_extra_claims(self, jwt_service, user_data):
        """Teste de token com claims adicionais"""
        extra_claims = {
            "role": "admin",
            "permissions": ["read", "write"]
        }
        
        token = jwt_service.create_access_token(
            user_id=user_data["user_id"],
            email=user_data["email"],
            username=user_data["username"],
            extra_claims=extra_claims
        )
        
        payload = jwt_service.decode_token(token)
        assert payload.extra_claims["role"] == "admin"
        assert payload.extra_claims["permissions"] == ["read", "write"]
    
    def test_token_expiration_check(self, jwt_service, user_data):
        """Teste básico de verificação de expiração"""
        token = jwt_service.create_access_token(
            user_id=user_data["user_id"],
            email=user_data["email"],
            username=user_data["username"]
        )
        
        # Token recém criado não deve estar expirado
        assert not jwt_service.is_token_expired(token)
        
        # Verificar se consegue obter a data de expiração
        exp_date = jwt_service.get_token_expiration(token)
        assert isinstance(exp_date, datetime)
        assert exp_date > datetime.now(timezone.utc)
    
    def test_userid_object_compatibility(self, jwt_service, user_data):
        """Teste de compatibilidade com objeto UserId"""
        user_id_obj = UserId(UUID(user_data["user_id"]))
        
        token = jwt_service.create_access_token(
            user_id=user_id_obj,  # Passando objeto UserId
            email=user_data["email"],
            username=user_data["username"]
        )
        
        payload = jwt_service.decode_token(token)
        assert payload.sub == str(user_id_obj)


# Teste de integração simples
def test_complete_jwt_flow():
    """Teste de fluxo completo JWT"""
    jwt_service = JWTService()
    
    user_data = {
        "user_id": "test-user-123",
        "email": "test@example.com",
        "username": "testuser"
    }
    
    # 1. Criar par de tokens
    tokens = jwt_service.create_token_pair(**user_data)
    
    # 2. Verificar access token
    access_payload = jwt_service.decode_token(tokens.access_token)
    assert access_payload.sub == user_data["user_id"]
    assert access_payload.token_type == "access"
    
    # 3. Verificar refresh token
    refresh_payload = jwt_service.decode_token(tokens.refresh_token)
    assert refresh_payload.sub == user_data["user_id"]
    assert refresh_payload.token_type == "refresh"
    
    # 4. Renovar access token
    new_access_token = jwt_service.refresh_access_token(tokens.refresh_token)
    new_payload = jwt_service.decode_token(new_access_token)
    assert new_payload.sub == user_data["user_id"]
    assert new_payload.token_type == "access"
    
    # 5. Extrair user_id
    extracted_id = jwt_service.get_user_id_from_token(new_access_token)
    assert extracted_id == user_data["user_id"]
    
    print("Fluxo JWT completo funcionando corretamente!")


if __name__ == "__main__":
    # Executar teste de integração diretamente
    test_complete_jwt_flow()
    print("Todos os testes básicos passaram!")