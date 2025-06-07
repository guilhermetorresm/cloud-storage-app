import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from cloud_storage_app.application.use_cases.user.create_user_use_case import CreateUserUseCase
from cloud_storage_app.application.dtos.user_dtos import CreateUserDTO, UserResponseDTO
from cloud_storage_app.presentation.schemas.user_schema import UserCreateSchema, UserResponseSchema
from cloud_storage_app.domain.exceptions.user_exceptions import (
    UserAlreadyExistsException,
    UserValidationException,
    InvalidPasswordException
)
from cloud_storage_app.infrastructure.di.container import get_database_session, get_container

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


# Função helper para obter o caso de uso
def get_create_user_use_case() -> CreateUserUseCase:
    """Factory para obter o caso de uso do container"""
    container = get_container()
    return container.create_user_use_case()


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