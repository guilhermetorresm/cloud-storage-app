import logging
from typing import List, Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status

from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from cloud_storage_app.application.dtos.file_dtos import (
    UploadFileInputDTO, FileUploadResponseDTO,
    ListUserFilesInputDTO, FileListResponseDTO,
    UpdateFileMetadataInputDTO, FileResponseDTO
)
from cloud_storage_app.application.use_cases.files import (
    UploadFileUseCase, ListUserFilesUseCase, UpdateFileMetadataUseCase
)
from cloud_storage_app.application.exceptions import (
    AuthenticationException,
    UserNotFoundException,
    ValidationException
)
from cloud_storage_app.domain.exceptions import FileValidationException, FileUploadException

from cloud_storage_app.infrastructure.di.container import get_container, get_database_session, get_storage_service
from cloud_storage_app.domain.value_objects import UserId

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/files", tags=["files"])

security = HTTPBearer()

# Função helper para obter o caso de uso
def get_list_user_files_use_case() -> ListUserFilesUseCase:
    """Factory para obter o caso de uso do container"""
    container = get_container()
    return container.list_user_files_use_case()

def get_upload_file_use_case() -> UploadFileUseCase:
    """Factory para obter o caso de uso do container"""
    container = get_container()
    return container.upload_file_use_case()

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
    "/upload", 
    response_model=FileUploadResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Fazer upload de arquivo",
    description="Endpoint para fazer upload de arquivos com processamento de mídia e geração de thumbnails",
    responses={
        201: {
            "description": "Arquivo enviado com sucesso",
            "model": FileUploadResponseDTO
        },
        400: {
            "description": "Arquivo inválido ou erro de processamento",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Tipo de arquivo não suportado",
                        "error_type": "FileValidationException"
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
async def upload_file(
    # Use Form para os metadados e File para o arquivo
    file: UploadFile = File(..., description="O arquivo a ser enviado."),
    description: Optional[str] = Form(None, description="Descrição do arquivo."),
    tags: Optional[List[str]] = Form(None, description="Tags para o arquivo."),

    # Injeção de dependências do container e da requisição
    access_token: str = Depends(extract_bearer_token),
    upload_use_case: UploadFileUseCase = Depends(get_upload_file_use_case),
    db_session = Depends(get_database_session),
    s3_service = Depends(get_storage_service)
):
    """
    Endpoint para upload de arquivos.
    - Recebe o arquivo e metadados via multipart/form-data.
    - Utiliza o UploadFileUseCase para orquestrar a lógica de negócio.
    - Trata exceções específicas e retorna os códigos HTTP apropriados.
    """
    try:
        # Cria o DTO de entrada com os dados recebidos
        upload_dto = UploadFileInputDTO(
            file_name=file.filename,
            file_size=file.size,
            mime_type=file.content_type,
            file_object=file.file, # Passa o objeto de arquivo diretamente
            description=description,
            tags=tags
        )
        
        # Executa o caso de uso com as dependências da requisição
        result_dto = await upload_use_case.execute(
            upload_dto=upload_dto,
            access_token=access_token,
            db_session=db_session,
            storage_service=s3_service
        )
        return result_dto

    except (ValidationException, FileValidationException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except (AuthenticationException, UserNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except FileUploadException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        # Captura genérica para erros inesperados
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro inesperado: {e}")


@router.get(
    "/list",
    response_model=FileListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Listar arquivos do usuário",
    description="Endpoint para listar arquivos do usuário autenticado com filtros e paginação",
    responses={
        200: {
            "description": "Lista de arquivos obtida com sucesso",
            "model": FileListResponseDTO
        },
        400: {
            "description": "Parâmetros de filtro inválidos",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Tipo de arquivo deve ser 'audio', 'image' ou 'video'",
                        "error_type": "ValidationException"
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
async def list_user_files(
    page: int = 1,
    page_size: int = 20,
    file_type: str = None,
    tags: str = None,  # Tags separadas por vírgulas
    file_name: str = None,
    access_token: str = Depends(extract_bearer_token),
    list_user_files_use_case: ListUserFilesUseCase = Depends(get_list_user_files_use_case),
    db: AsyncSession = Depends(get_database_session)
) -> FileListResponseDTO:
    """
    Lista arquivos do usuário autenticado com filtros e paginação.
    
    Este endpoint permite listar arquivos do usuário autenticado com diversos filtros:
    - Paginação (página e tamanho da página)
    - Filtro por tipo de arquivo (audio, image, video)
    - Filtro por tags (separadas por vírgulas)
    - Filtro por nome do arquivo
    
    Args:
        page: Número da página (padrão: 1)
        page_size: Tamanho da página (padrão: 20, máximo: 100)
        file_type: Tipo de arquivo para filtro ('audio', 'image', 'video')
        tags: Tags separadas por vírgulas para filtro
        file_name: Nome do arquivo para filtro (busca parcial)
        access_token: Token de acesso extraído do cabeçalho Authorization
        list_user_files_use_case: Caso de uso injetado para listagem de arquivos
        db: Sessão do banco de dados injetada
        
    Returns:
        FileListResponseDTO: Lista paginada de arquivos com metadados
        
    Raises:
        HTTPException:
            - 400: Parâmetros de filtro inválidos
            - 401: Token inválido, expirado ou usuário não encontrado
            - 422: Dados de entrada inválidos
            - 500: Erro interno do servidor
    """
    try:
        logger.info("Recebida requisição para listar arquivos do usuário")
        
        # Processar tags de filtro
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Criar DTO de request
        list_dto = ListUserFilesInputDTO(
            page=page,
            page_size=page_size,
            file_type=file_type,
            tags=tag_list,
            file_name=file_name
        )
        
        # Executar caso de uso
        result = await list_user_files_use_case.execute(
            request=list_dto,
            access_token=access_token,
            db_session=db
        )
        
        logger.info(f"Listagem retornou {len(result.files)} arquivos da página {page}")
        return result
        
    except ValidationException as e:
        logger.warning(f"Erro de validação na listagem: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
            headers={"error_type": "ValidationException"}
        )
        
    except FileValidationException as e:
        logger.warning(f"Erro de validação de arquivo na listagem: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
            headers={"error_type": "FileValidationException"}
        )
        
    except AuthenticationException as e:
        logger.warning(f"Erro de autenticação na listagem: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    except UserNotFoundException as e:
        logger.warning(f"Usuário não encontrado na listagem: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    except ValueError as e:
        logger.error(f"Dados inválidos na listagem: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
        
    except Exception as e:
        logger.error(f"Erro inesperado na listagem: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.put("/{file_id}/metadata", response_model=FileResponseDTO)
async def update_file_metadata(
    file_id: str,
    new_name: str = None,
    new_description: str = None,
    new_tags: str = None  # Tags separadas por vírgulas
    # current_user_id: str = Depends(get_current_user_id),
    # db_session: AsyncSession = Depends(get_db_session)
):
    """
    Atualiza metadados de um arquivo.
    
    Args:
        file_id: ID do arquivo
        new_name: Novo nome do arquivo
        new_description: Nova descrição
        new_tags: Novas tags separadas por vírgulas
        current_user_id: ID do usuário autenticado
        db_session: Sessão do banco de dados
        
    Returns:
        FileResponseDTO: Dados atualizados do arquivo
    """
    try:
        # Processar tags
        tag_list = []
        if new_tags:
            tag_list = [tag.strip() for tag in new_tags.split(",") if tag.strip()]
        
        # Criar DTO
        update_dto = UpdateFileMetadataInputDTO(
            file_id=file_id,
            new_name=new_name,
            new_description=new_description,
            new_tags=tag_list
        )
        
        # Executar caso de uso
        use_case = UpdateFileMetadataUseCase()
        owner_id = UserId.from_string(current_user_id)
        
        result = await use_case.execute(update_dto, owner_id, db_session)
        
        logger.info(f"Metadados atualizados com sucesso: {file_id}")
        return result
        
    except Exception as e:
        logger.error(f"Erro na atualização: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e)) 