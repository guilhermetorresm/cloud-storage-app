import logging
from typing import Dict, Any, Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from cloud_storage_app.application.use_cases.user.create_user_use_case import CreateUserUseCase
from cloud_storage_app.application.use_cases.user.get_current_user_use_case import GetCurrentUserUseCase
from cloud_storage_app.application.dtos.user_dtos import CreateUserDTO, UserResponseDTO, GetUsersMeDTO
from cloud_storage_app.application.use_cases.user.change_password_use_case import ChangePasswordUseCase
from cloud_storage_app.presentation.schemas.user_schema import UserCreateSchema, UserResponseSchema
from cloud_storage_app.presentation.schemas.user_schema import ChangePasswordSchema
from cloud_storage_app.domain.exceptions.user_exceptions import (
    UserAlreadyExistsException,
    UserValidationException,
    InvalidPasswordException,
)
from cloud_storage_app.application.exceptions import (
    AuthenticationException,
    UserNotFoundException
)

from cloud_storage_app.infrastructure.di.container import get_database_session, get_container, get_password_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

security = HTTPBearer()

# Função helper para obter o caso de uso
def get_create_user_use_case() -> CreateUserUseCase:
    """Factory para obter o caso de uso do container"""
    container = get_container()
    return container.create_user_use_case()

def get_get_current_user_use_case() -> GetCurrentUserUseCase:
    """Factory para obter o caso de uso do container"""
    container = get_container()
    return container.get_current_user_use_case()

def get_change_password_use_case() -> ChangePasswordUseCase:
    """Factory para obter o caso de uso do container"""
    container = get_container()
    return container.change_password_use_case()

def extract_bearer_token(authorization: Annotated[str, Depends(security)]) -> str:
    """
    Extrai o token do cabeçalho Authorization Bearer.
    
    Args:
        authorization: Token de autorização no formato Bearer
        
    Returns:
        str: Token extraído sem o prefixo "Bearer "
        
    Raises:
        HTTPException: Se o token não for fornecido ou formato inválido
    """
    if not authorization.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso é obrigatório",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return authorization.credentials

@router.post(
    "/",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo usuário",
    description="Endpoint para criar um novo usuário no sistema",
    responses={
        201: {
            "description": "Usuário criado com sucesso",
            "model": UserResponseSchema
        },
        400: {
            "description": "Dados inválidos ou usuário já existe",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Username já está em uso",
                        "error_type": "UserAlreadyExistsException"
                    }
                }
            }
        },
        422: {
            "description": "Erro de validação nos dados fornecidos",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Email deve ter um formato válido",
                        "error_type": "UserValidationException"
                    }
                }
            }
        },
        500: {
            "description": "Erro interno do servidor"
        }
    }
)
async def create_user(
    user_data: UserCreateSchema,
    create_user_use_case: CreateUserUseCase = Depends(get_create_user_use_case),
    db: AsyncSession = Depends(get_database_session)
) -> UserResponseSchema:
    """
    Criar um novo usuário no sistema.
    
    Este endpoint recebe os dados do usuário, valida e cria um novo registro
    no sistema através do caso de uso CreateUserUseCase.
    
    Args:
        user_data: Dados do usuário a ser criado
        db: Sessão do banco de dados
        create_user_use_case: Caso de uso injetado para criação de usuário
        
    Returns:
        UserResponseSchema: Dados do usuário criado
        
    Raises:
        HTTPException: Em caso de erro de validação ou usuário já existente
    """
    logger.info(f"Recebida requisição para criar usuário com email: {user_data.email}")
    
    try:
        # Converter schema de request para DTO
        create_user_dto = CreateUserDTO(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        
        # Executar caso de uso passando a sessão
        user_response_dto = await create_user_use_case.execute(
            create_user_dto=create_user_dto,
            db_session=db
        )
        
        # Converter DTO de resposta para schema de response
        user_response = UserResponseSchema(
            user_id=user_response_dto.user_id,
            username=user_response_dto.username,
            email=user_response_dto.email,
            first_name=user_response_dto.first_name,
            last_name=user_response_dto.last_name,
            is_active=user_response_dto.is_active,
            created_at=user_response_dto.created_at,
            updated_at=user_response_dto.updated_at
        )
        
        logger.info(f"Usuário criado com sucesso: {user_response.username}")
        return user_response
        
    except UserAlreadyExistsException as e:
        logger.warning(f"Tentativa de criar usuário que já existe: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
            headers={"error_type": "UserAlreadyExistsException"}
        )
        
    except UserValidationException as e:
        logger.warning(f"Erro de validação ao criar usuário: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
            headers={"error_type": "UserValidationException"}
        )
        
    except InvalidPasswordException as e:
        logger.warning(f"Senha inválida ao criar usuário: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
            headers={"error_type": "InvalidPasswordException"}
        )
        
    except Exception as e:
        logger.error(f"Erro inesperado ao criar usuário: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get(
    "/me",
    response_model=UserResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Obter dados do usuário autenticado",
    description="Retorna os dados completos do usuário atualmente autenticado",
    responses={
        200: {
            "description": "Dados do usuário obtidos com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "username": "johndoe",
                        "email": "john@example.com",
                        "first_name": "John",
                        "last_name": "Doe",
                        "profile_picture": None,
                        "description": None,
                        "is_active": True,
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z",
                        "last_login_at": "2024-01-15T14:20:00Z"
                    }
                }
            }
        },
        401: {
            "description": "Token inválido, expirado ou usuário não encontrado",
            "content": {
                "application/json": {
                    "examples": {
                        "token_invalid": {
                            "summary": "Token inválido",
                            "value": {"detail": "Token inválido"}
                        },
                        "token_expired": {
                            "summary": "Token expirado",
                            "value": {"detail": "Token expirado"}
                        },
                        "user_not_found": {
                            "summary": "Usuário não encontrado",
                            "value": {"detail": "Usuário não encontrado"}
                        }
                    }
                }
            }
        },
        422: {
            "description": "Dados de entrada inválidos",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Token de acesso é obrigatório"
                    }
                }
            }
        },
        500: {
            "description": "Erro interno do servidor"
        }
    }
)
async def get_current_user(
    access_token: str = Depends(extract_bearer_token),
    get_current_user_use_case: GetCurrentUserUseCase = Depends(get_get_current_user_use_case),
    db: AsyncSession = Depends(get_database_session)
) -> UserResponseSchema:
    """
    Obter dados do usuário autenticado.
    
    Este endpoint decodifica o token JWT fornecido no cabeçalho Authorization
    e retorna os dados completos do usuário autenticado.
    
    Args:
        access_token: Token de acesso extraído do cabeçalho Authorization
        get_current_user_use_case: Caso de uso injetado para obter usuário atual
        db: Sessão do banco de dados injetada
        
    Returns:
        UserResponseSchema: Dados completos do usuário autenticado
        
    Raises:
        HTTPException: 
            - 401: Token inválido, expirado ou usuário não encontrado
            - 422: Dados de entrada inválidos
            - 500: Erro interno do servidor
    """
    try:
        logger.info("Recebida requisição para obter dados do usuário atual")
        
        # Criar DTO de request
        request_dto = GetUsersMeDTO(access_token=access_token)
        
        # Executar caso de uso
        user_response_dto = await get_current_user_use_case.execute(
            request=request_dto,
            db_session=db
        )
        
        # Converter DTO de resposta para schema de response
        user_response = UserResponseSchema(
            user_id=user_response_dto.user_id,
            username=user_response_dto.username,
            email=user_response_dto.email,
            first_name=user_response_dto.first_name,
            last_name=user_response_dto.last_name,
            profile_picture=user_response_dto.profile_picture,
            description=user_response_dto.description,
            is_active=user_response_dto.is_active,
            created_at=user_response_dto.created_at,
            updated_at=user_response_dto.updated_at,
            last_login_at=user_response_dto.last_login_at
        )
        
        logger.info(f"Dados do usuário atual obtidos com sucesso: {user_response.username}")
        return user_response
        
    except AuthenticationException as e:
        logger.warning(f"Erro de autenticação ao obter usuário atual: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    except UserNotFoundException as e:
        logger.warning(f"Usuário não encontrado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    except ValueError as e:
        logger.error(f"Dados inválidos ao obter usuário atual: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
        
    except Exception as e:
        logger.error(f"Erro inesperado ao obter usuário atual: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.patch(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Alterar senha do usuário",
    description="Endpoint para alterar a senha do usuário autenticado",
    responses={
        204: {
            "description": "Senha alterada com sucesso"
        },
        400: {
            "description": "Senha atual incorreta ou nova senha inválida",
            "content": {
                "application/json": {
                    "examples": {
                        "wrong_current_password": {
                            "summary": "Senha atual incorreta",
                            "value": {
                                "detail": "Senha atual incorreta",
                                "error_type": "InvalidPasswordException"
                            }
                        },
                        "same_password": {
                            "summary": "Nova senha igual à atual",
                            "value": {
                                "detail": "A nova senha deve ser diferente da senha atual",
                                "error_type": "UserValidationException"
                            }
                        }
                    }
                }
            }
        },
        401: {
            "description": "Token inválido, expirado ou usuário não encontrado",
            "content": {
                "application/json": {
                    "examples": {
                        "token_invalid": {
                            "summary": "Token inválido",
                            "value": {"detail": "Token inválido"}
                        },
                        "token_expired": {
                            "summary": "Token expirado",
                            "value": {"detail": "Token expirado"}
                        },
                        "user_not_found": {
                            "summary": "Usuário não encontrado",
                            "value": {"detail": "Usuário não encontrado"}
                        }
                    }
                }
            }
        },
        422: {
            "description": "Dados de entrada inválidos",
            "content": {
                "application/json": {
                    "examples": {
                        "validation_error": {
                            "summary": "Erro de validação",
                            "value": {
                                "detail": "Nova senha deve ter pelo menos 8 caracteres",
                                "error_type": "UserValidationException"
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "Erro interno do servidor"
        }
    }
)
async def change_password(
    password_data: ChangePasswordSchema,
    access_token: str = Depends(extract_bearer_token),
    change_password_use_case: ChangePasswordUseCase = Depends(get_change_password_use_case),
    db: AsyncSession = Depends(get_database_session)
) -> None:
    """
    Alterar senha do usuário autenticado.
    
    Este endpoint permite que um usuário autenticado altere sua senha,
    verificando a senha atual e validando a nova senha.
    
    Args:
        password_data: Dados contendo senha atual e nova senha
        access_token: Token de acesso extraído do cabeçalho Authorization
        change_password_use_case: Caso de uso injetado para alteração de senha
        db: Sessão do banco de dados injetada
        
    Raises:
        HTTPException:
            - 400: Senha atual incorreta ou nova senha inválida
            - 401: Token inválido, expirado ou usuário não encontrado
            - 422: Dados de entrada inválidos
            - 500: Erro interno do servidor
    """
    try:
        logger.info("Recebida requisição para alterar senha de usuário")
        
        # Converter schema para DTO
        change_password_dto = ChangePasswordDTO(
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        
        # Executar caso de uso
        await change_password_use_case.execute(
            access_token=access_token,
            change_password_dto=change_password_dto,
            db_session=db
        )
        
        logger.info("Senha alterada com sucesso")
        # Retorna 204 No Content - sem corpo de resposta
        
    except InvalidPasswordException as e:
        logger.warning(f"Senha atual incorreta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
            headers={"error_type": "InvalidPasswordException"}
        )
        
    except UserValidationException as e:
        logger.warning(f"Erro de validação na alteração de senha: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
            headers={"error_type": "UserValidationException"}
        )
        
    except AuthenticationException as e:
        logger.warning(f"Erro de autenticação na alteração de senha: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    except UserNotFoundException as e:
        logger.warning(f"Usuário não encontrado na alteração de senha: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    except ValueError as e:
        logger.error(f"Dados inválidos na alteração de senha: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
        
    except Exception as e:
        logger.error(f"Erro inesperado na alteração de senha: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )