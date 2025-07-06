import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from cloud_storage_app.application.dtos.file_dtos import (
    UploadFileInputDTO, FileUploadResponseDTO,
    ListUserFilesInputDTO, FileListResponseDTO,
    UpdateFileMetadataInputDTO, FileResponseDTO
)
from cloud_storage_app.application.use_cases.files import (
    UploadFileUseCase, ListUserFilesUseCase, UpdateFileMetadataUseCase
)
from cloud_storage_app.infrastructure.database.connection import get_db_session
from cloud_storage_app.infrastructure.storage.s3_storage_service import S3StorageService
from cloud_storage_app.shared.auth_utils import get_current_user_id
from cloud_storage_app.domain.value_objects import UserId

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/files", tags=["files"])

@router.post("/upload", response_model=FileUploadResponseDTO)
async def upload_file(
    file: UploadFile = File(...),
    description: str = Form(None),
    tags: str = Form(None),  # Tags como string separada por vírgulas
    current_user_id: str = Depends(get_current_user_id),
    db_session: AsyncSession = Depends(get_db_session),
    storage_service: S3StorageService = Depends()
):
    """
    Faz upload de um arquivo com tags e descrição.
    
    Args:
        file: Arquivo a ser enviado
        description: Descrição opcional do arquivo
        tags: Tags separadas por vírgulas (ex: "música,rock,2024")
        current_user_id: ID do usuário autenticado
        db_session: Sessão do banco de dados
        storage_service: Serviço de armazenamento
        
    Returns:
        FileUploadResponseDTO: Dados do arquivo criado
    """
    try:
        # Processar tags
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Criar DTO
        upload_dto = UploadFileInputDTO(
            file_name=file.filename,
            file_size=file.size,
            mime_type=file.content_type,
            file_object=file.file,
            description=description,
            tags=tag_list
        )
        
        # Executar caso de uso
        use_case = UploadFileUseCase()
        owner_id = UserId.from_string(current_user_id)
        
        result = await use_case.execute(upload_dto, owner_id, db_session, storage_service)
        
        logger.info(f"Arquivo enviado com sucesso: {result.file_id}")
        return result
        
    except Exception as e:
        logger.error(f"Erro no upload: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/list", response_model=FileListResponseDTO)
async def list_user_files(
    page: int = 1,
    page_size: int = 20,
    file_type: str = None,
    tags: str = None,  # Tags separadas por vírgulas
    file_name: str = None,
    current_user_id: str = Depends(get_current_user_id),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Lista arquivos do usuário com filtros.
    
    Args:
        page: Número da página
        page_size: Tamanho da página
        file_type: Tipo de arquivo (audio, image, video)
        tags: Tags separadas por vírgulas para filtro
        file_name: Nome do arquivo para filtro
        current_user_id: ID do usuário autenticado
        db_session: Sessão do banco de dados
        
    Returns:
        FileListResponseDTO: Lista paginada de arquivos
    """
    try:
        # Processar tags de filtro
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Criar DTO
        list_dto = ListUserFilesInputDTO(
            user_id=current_user_id,
            page=page,
            page_size=page_size,
            file_type=file_type,
            tags=tag_list,
            file_name=file_name
        )
        
        # Executar caso de uso
        use_case = ListUserFilesUseCase()
        result = await use_case.execute(list_dto, db_session)
        
        logger.info(f"Listagem retornou {len(result.files)} arquivos")
        return result
        
    except Exception as e:
        logger.error(f"Erro na listagem: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{file_id}/metadata", response_model=FileResponseDTO)
async def update_file_metadata(
    file_id: str,
    new_name: str = None,
    new_description: str = None,
    new_tags: str = None,  # Tags separadas por vírgulas
    current_user_id: str = Depends(get_current_user_id),
    db_session: AsyncSession = Depends(get_db_session)
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