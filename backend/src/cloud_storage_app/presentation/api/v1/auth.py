import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from cloud_storage_app.application.use_cases.auth.login_use_case import LoginUseCase
from cloud_storage_app.application.dtos.user_dtos import UserLoginDTO, UserLoginResponseDTO
from cloud_storage_app.application.exceptions import (
    AuthenticationException,
    InvalidCredentialsException,
    UserNotFoundException
)
from cloud_storage_app.infrastructure.di.container import (
    get_container,
    get_database_session
)

logger = logging.getLogger(__name__)

# Configuração do router
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        401: {"description": "Credenciais inválidas"},
        422: {"description": "Dados de entrada inválidos"},
        500: {"description": "Erro interno do servidor"}
    }
)

# Security scheme para documentação
security = HTTPBearer()


# ==========================================
# DEPENDENCIES
# ==========================================

async def get_login_use_case(
    db_session: Annotated[AsyncSession, Depends(get_database_session)]
) -> LoginUseCase:
    """
    Dependency para obter instância do LoginUseCase.
    
    Args:
        db_session: Sessão do banco de dados
        
    Returns:
        LoginUseCase: Instância configurada do caso de uso
    """
    container = get_container()
    
    # Criar repositório com a sessão
    from cloud_storage_app.infrastructure.database.repositories.user_repository import UserRepository
    user_repository = UserRepository(session=db_session)
    
    # Obter serviços do container
    password_service = container.password_service()
    jwt_service = container.jwt_service()
    
    # Criar caso de uso com todas as dependências
    return LoginUseCase(
        user_repository=user_repository,
        password_service=password_service,
        jwt_service=jwt_service
    )


# ==========================================
# ENDPOINTS
# ==========================================

@router.post(
    "/login",
    response_model=UserLoginResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Autenticar usuário",
    description="Realiza login do usuário e retorna tokens JWT",
    responses={
        200: {
            "description": "Login realizado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "token_type": "Bearer",
                        "user": {
                            "user_id": "123e4567-e89b-12d3-a456-426614174000",
                            "username": "johndoe",
                            "email": "john@example.com",
                            "first_name": "John",
                            "last_name": "Doe"
                        }
                    }
                }
            }
        },
        401: {
            "description": "Credenciais inválidas",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Username ou Senha inválidos"
                    }
                }
            }
        },
        422: {
            "description": "Dados de entrada inválidos",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "username"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def login(
    login_data: UserLoginDTO,
    login_use_case: Annotated[LoginUseCase, Depends(get_login_use_case)]
) -> UserLoginResponseDTO:
    """
    Endpoint para autenticação de usuários.
    
    Realiza o login validando as credenciais fornecidas e retorna
    tokens JWT (access + refresh) junto com informações básicas do usuário.
    
    Args:
        login_data: Dados de login (username e password)
        login_use_case: Caso de uso de login injetado
        db_session: Sessão do banco de dados injetada
        
    Returns:
        UserLoginResponseDTO: Dados de resposta com tokens e informações do usuário
        
    Raises:
        HTTPException: 
            - 401: Credenciais inválidas ou usuário não encontrado
            - 422: Dados de entrada inválidos
            - 500: Erro interno do servidor
    """
    try:
        logger.info(f"Tentativa de login - Username: {login_data.username}")
        
        # Executar caso de uso de login
        response = await login_use_case.execute(login_data)
        
        logger.info(f"Login realizado com sucesso - Username: {login_data.username}")
        return response
        
    except InvalidCredentialsException as e:
        logger.warning(f"Credenciais inválidas para username: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
        
    except UserNotFoundException as e:
        logger.warning(f"Usuário não encontrado: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou Senha inválidos"  # Não expor informação sobre existência do usuário
        )
        
    except AuthenticationException as e:
        logger.error(f"Erro de autenticação: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erro na autenticação"
        )
        
    except ValueError as e:
        logger.error(f"Dados inválidos no login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
        
    except Exception as e:
        logger.error(f"Erro inesperado no login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.post(
    "/refresh",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Renovar token de acesso",
    description="Gera um novo access token usando um refresh token válido",
    responses={
        200: {
            "description": "Token renovado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "token_type": "Bearer"
                    }
                }
            }
        },
        401: {"description": "Refresh token inválido ou expirado"}
    }
)
async def refresh_token(
    refresh_token: str,
    login_use_case: Annotated[LoginUseCase, Depends(get_login_use_case)]
) -> dict:
    """
    Endpoint para renovação de access token.
    
    Args:
        refresh_token: Refresh token válido
        login_use_case: Caso de uso de login injetado
        
    Returns:
        dict: Novo access token
        
    Raises:
        HTTPException: 401 se o refresh token for inválido
    """
    try:
        # Usar o serviço JWT diretamente do caso de uso
        jwt_service = login_use_case._jwt_service
        new_access_token = jwt_service.refresh_access_token(refresh_token)
        
        return {
            "access_token": new_access_token,
            "token_type": "Bearer"
        }
        
    except Exception as e:
        logger.error(f"Erro ao renovar token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado"
        )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout do usuário",
    description="Invalida os tokens do usuário (implementação futura)",
    responses={
        200: {"description": "Logout realizado com sucesso"}
    }
)
async def logout(
    token: Annotated[str, Depends(security)]
) -> dict:
    """
    Endpoint para logout (implementação básica).
    
    Em uma implementação completa, seria necessário:
    - Blacklist dos tokens
    - Invalidação no cache/redis
    - Log de auditoria
    
    Args:
        token: Token de autorização
        
    Returns:
        dict: Mensagem de sucesso
    """
    try:
        # TODO: Implementar blacklist de tokens
        # TODO: Invalidar tokens no cache/redis
        # TODO: Registrar evento de logout
        
        logger.info("Logout realizado")
        return {"message": "Logout realizado com sucesso"}
        
    except Exception as e:
        logger.error(f"Erro no logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )
