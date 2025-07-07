"""
Caso de uso para listagem de arquivos do usuário autenticado.
Responsável por validar token JWT e listar arquivos com filtros e paginação.
"""

import logging
from typing import List, Optional
from dataclasses import dataclass

from dependency_injector.wiring import Provide, inject
from sqlalchemy.ext.asyncio import AsyncSession

from cloud_storage_app.domain.entities.user import User
from cloud_storage_app.infrastructure.database.repositories.user_repository import UserRepository
from cloud_storage_app.infrastructure.database.repositories import (
    AudioFileRepository, ImageFileRepository, VideoFileRepository
)
from cloud_storage_app.domain.value_objects.user_id import UserId
from cloud_storage_app.infrastructure.auth.jwt_service import JWTService, TokenPayload
from cloud_storage_app.application.dtos.file_dtos import (
    ListUserFilesInputDTO, FileListResponseDTO, FileResponseDTO,
    entity_to_file_response_dto
)

# Exceções da camada de aplicação
from cloud_storage_app.application.exceptions import (
    ApplicationException,
    AuthenticationException,
    ValidationException,
    InvalidTokenException,
    ExpiredTokenException
)

# Exceções do domínio - prioritárias
from cloud_storage_app.domain.exceptions import (
    UserNotFoundException,
    UserValidationException,
    UserInactiveException,
    FileValidationException,
    FileNotFoundException
)

# Exceções da infraestrutura de JWT
from cloud_storage_app.infrastructure.auth import (
    JWTException
)

logger = logging.getLogger(__name__)


class ListUserFilesUseCase:
    """
    Caso de uso para listagem de arquivos do usuário autenticado.
    
    Responsabilidades:
    - Decodificar e validar token JWT
    - Validar parâmetros de listagem e filtros
    - Buscar arquivos do usuário com filtros aplicados
    - Aplicar paginação
    - Retornar lista paginada de arquivos
    - Tratar erros de token inválido ou expirado
    """
    
    @inject
    def __init__(
        self,
        jwt_service: JWTService,
    ):
        self._jwt_service = jwt_service
        self._db_session = None  # Será definida no execute()
        self._user_repository = None  # Será criada no execute()
        self._audio_repository = None  # Será criada no execute()
        self._image_repository = None  # Será criada no execute()
        self._video_repository = None  # Será criada no execute()
        logger.debug("ListUserFilesUseCase inicializado")
    
    async def execute(
        self, 
        request: ListUserFilesInputDTO, 
        access_token: str, 
        db_session: AsyncSession
    ) -> FileListResponseDTO:
        """
        Executa o caso de uso para listagem de arquivos do usuário.
        
        Args:
            request: ListUserFilesInputDTO contendo filtros e parâmetros de paginação
            access_token: Token JWT de acesso
            db_session: Sessão do banco de dados
            
        Returns:
            FileListResponseDTO: Lista paginada de arquivos
            
        Raises:
            AuthenticationException: Se o token for inválido, expirado ou usuário não encontrado
            ValidationException: Se os parâmetros de listagem forem inválidos
            FileValidationException: Se houver erro na busca de arquivos
            UserNotFoundException: Se o usuário não for encontrado
            UserInactiveException: Se o usuário estiver inativo
        """
        self._db_session = db_session
        self._user_repository = UserRepository(session=db_session)
        self._audio_repository = AudioFileRepository(session=db_session)
        self._image_repository = ImageFileRepository(session=db_session)
        self._video_repository = VideoFileRepository(session=db_session)

        try:
            logger.debug("Iniciando processo de listagem de arquivos")
            
            # 1. Validar entrada
            self._validate_request(request, access_token)
            
            # 2. Decodificar e validar token JWT
            token_payload = await self._decode_and_validate_token(access_token)
            
            # 3. Buscar usuário no repositório
            user = await self._find_user_by_id(token_payload.sub)
            
            # 4. Verificar status do usuário
            self._check_user_status(user)
            
            # 5. Buscar e filtrar arquivos
            file_list_response = await self._list_user_files(user.user_id, request)
            
            logger.info(f"Listagem de arquivos concluída para usuário: {user.username.value}")
            return file_list_response
            
        except (
            AuthenticationException, 
            ValidationException, 
            UserNotFoundException, 
            UserInactiveException, 
            FileValidationException,
            InvalidTokenException,
            ExpiredTokenException
        ):
            # Re-raise exceções conhecidas
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao listar arquivos: {str(e)}")
            logger.debug(f"Detalhes do erro: {e.__class__.__name__}: {str(e)}")
            raise ApplicationException("Erro interno na listagem de arquivos") from e
    
    def _validate_request(self, request: ListUserFilesInputDTO, access_token: str) -> None:
        """
        Valida os dados de entrada do request.
        
        Args:
            request: Request com parâmetros de listagem
            access_token: Token JWT de acesso
            
        Raises:
            AuthenticationException: Se o token estiver inválido
            ValidationException: Se os parâmetros de listagem forem inválidos
        """
        if not access_token or not access_token.strip():
            logger.warning("Token de acesso não fornecido")
            raise AuthenticationException("Token de acesso é obrigatório")
        
        # Verificar formato básico do token
        token_parts = access_token.strip().split('.')
        if len(token_parts) != 3:
            logger.warning("Token de acesso com formato inválido")
            raise AuthenticationException("Formato de token inválido")
        
        # Validar parâmetros de paginação
        if request.page < 1:
            logger.warning(f"Número de página inválido: {request.page}")
            raise ValidationException(
                "Número da página deve ser maior que 0",
                details={"field": "page", "value": request.page}
            )
        
        if request.page_size < 1 or request.page_size > 100:
            logger.warning(f"Tamanho de página inválido: {request.page_size}")
            raise ValidationException(
                "Tamanho da página deve estar entre 1 e 100",
                details={"field": "page_size", "value": request.page_size}
            )
        
        # Validar tipo de arquivo se especificado
        if request.file_type and request.file_type not in ['audio', 'image', 'video']:
            logger.warning(f"Tipo de arquivo inválido: {request.file_type}")
            raise ValidationException(
                "Tipo de arquivo deve ser 'audio', 'image' ou 'video'",
                details={"field": "file_type", "value": request.file_type}
            )
        
        # Validar tags se especificadas
        if request.tags and len(request.tags) > 10:
            logger.warning(f"Muitas tags especificadas: {len(request.tags)}")
            raise ValidationException(
                "Máximo de 10 tags permitidas para filtro",
                details={"field": "tags", "value": len(request.tags)}
            )
        
        logger.debug("Parâmetros de request validados com sucesso")
    
    async def _decode_and_validate_token(self, access_token: str) -> TokenPayload:
        """
        Decodifica e valida o token JWT.
        
        Args:
            access_token: Token JWT de acesso
            
        Returns:
            TokenPayload: Payload decodificado do token
            
        Raises:
            AuthenticationException: Se o token for inválido ou expirado
            InvalidTokenException: Se o token for inválido
            ExpiredTokenException: Se o token estiver expirado
        """
        try:
            logger.debug("Decodificando token JWT")
            
            # Decodificar token
            token_payload = self._jwt_service.decode_token(access_token)
            
            # Validar se é um access token
            if not self._jwt_service.validate_token_type(token_payload, "access"):
                logger.warning("Token fornecido não é um access token")
                raise InvalidTokenException("Tipo de token inválido")
            
            logger.debug(f"Token decodificado com sucesso para usuário: {token_payload.sub}")
            return token_payload
            
        except ExpiredTokenException as e:
            logger.warning(f"Token expirado: {str(e)}")
            raise ExpiredTokenException("Token expirado") from e
            
        except InvalidTokenException as e:
            logger.warning(f"Token inválido: {str(e)}")
            raise InvalidTokenException("Token inválido") from e
            
        except JWTException as e:
            logger.error(f"Erro JWT: {str(e)}")
            raise AuthenticationException("Erro ao processar token") from e
            
        except Exception as e:
            logger.error(f"Erro inesperado ao decodificar token: {str(e)}")
            raise AuthenticationException("Erro interno ao processar token") from e
    
    async def _find_user_by_id(self, user_id_str: str) -> User:
        """
        Busca usuário pelo ID extraído do token.
        
        Args:
            user_id_str: String do ID do usuário
            
        Returns:
            User: Entidade do usuário encontrado
            
        Raises:
            UserNotFoundException: Se o usuário não for encontrado
            UserValidationException: Se o ID do usuário for inválido
            AuthenticationException: Para outros erros de busca
        """
        try:
            logger.debug(f"Buscando usuário por ID: {user_id_str}")
            
            user_id = UserId.from_string(user_id_str)
            user = await self._user_repository.find_by_id(user_id)
            
            if not user:
                logger.warning(f"Usuário não encontrado para ID: {user_id_str}")
                raise UserNotFoundException(user_id_str)
            
            logger.debug(f"Usuário encontrado: {user.username.value}")
            return user
            
        except UserNotFoundException:
            raise
        except ValueError as e:
            logger.error(f"ID de usuário inválido: {str(e)}")
            raise UserValidationException(
                "ID de usuário inválido no token",
                field="user_id",
                value=user_id_str
            ) from e
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por ID: {str(e)}")
            raise AuthenticationException("Erro ao buscar dados do usuário") from e
    
    def _check_user_status(self, user: User) -> None:
        """
        Verifica se o usuário está em status válido.
        
        Args:
            user: Entidade do usuário
            
        Raises:
            UserInactiveException: Se o usuário estiver inativo
            AuthenticationException: Se o usuário não puder ser autenticado
        """
        if not user:
            raise AuthenticationException("Status de usuário inválido")
        
        if hasattr(user, 'is_active') and not user.is_active:
            logger.warning(f"Tentativa de listagem com usuário inativo: {user.username.value}")
            raise UserInactiveException(str(user.user_id))
        
        logger.debug(f"Status do usuário {user.username.value} verificado com sucesso")
    
    async def _list_user_files(self, owner_id: UserId, request: ListUserFilesInputDTO) -> FileListResponseDTO:
        """
        Lista arquivos do usuário com filtros e paginação.
        
        Args:
            owner_id: ID do proprietário dos arquivos
            request: Parâmetros de listagem e filtros
            
        Returns:
            FileListResponseDTO: Lista paginada de arquivos
            
        Raises:
            FileValidationException: Se houver erro na busca de arquivos
        """
        try:
            logger.info(f"Listando arquivos do usuário: {owner_id}")
            logger.debug(f"Filtros aplicados: type={request.file_type}, tags={request.tags}, name={request.file_name}")
            
            # 1. Buscar arquivos por tipo
            all_files = await self._fetch_files_by_type(owner_id, request.file_type)
            
            # 2. Aplicar filtros
            filtered_files = self._apply_filters(all_files, request)
            
            # 3. Ordenar por data de criação (mais recentes primeiro)
            filtered_files.sort(key=lambda x: x.created_at, reverse=True)
            
            # 4. Aplicar paginação
            paginated_result = self._apply_pagination(filtered_files, request)
            
            # 5. Converter para DTOs
            file_dtos = [self._entity_to_dto(file_entity) for file_entity in paginated_result['files']]
            
            logger.info(f"Retornando {len(file_dtos)} arquivos da página {request.page}")
            
            # 6. Retornar resposta
            return FileListResponseDTO(
                files=file_dtos,
                total_count=paginated_result['total_count'],
                page=request.page,
                page_size=request.page_size,
                total_pages=paginated_result['total_pages']
            )
            
        except Exception as e:
            logger.error(f"Erro na listagem de arquivos: {str(e)}")
            raise FileValidationException(f"Erro interno na listagem de arquivos: {str(e)}") from e
    
    async def _fetch_files_by_type(self, owner_id: UserId, file_type: Optional[str]) -> List:
        """
        Busca arquivos baseado no tipo especificado.
        
        Args:
            owner_id: ID do proprietário
            file_type: Tipo de arquivo ('audio', 'image', 'video') ou None para todos
            
        Returns:
            List: Lista de entidades de arquivo
            
        Raises:
            FileValidationException: Se houver erro na busca de arquivos
        """
        all_files = []
        
        try:
            # Buscar arquivos baseado no tipo
            if file_type is None or file_type == 'audio':
                audio_files = await self._audio_repository.find_by_owner_id(owner_id)
                all_files.extend(audio_files)
                logger.debug(f"Encontrados {len(audio_files)} arquivos de áudio")
            
            if file_type is None or file_type == 'image':
                image_files = await self._image_repository.find_by_owner_id(owner_id)
                all_files.extend(image_files)
                logger.debug(f"Encontrados {len(image_files)} arquivos de imagem")
            
            if file_type is None or file_type == 'video':
                video_files = await self._video_repository.find_by_owner_id(owner_id)
                all_files.extend(video_files)
                logger.debug(f"Encontrados {len(video_files)} arquivos de vídeo")
            
            logger.debug(f"Total de arquivos encontrados: {len(all_files)}")
            return all_files
            
        except Exception as e:
            logger.error(f"Erro ao buscar arquivos por tipo: {str(e)}")
            raise FileValidationException("Erro ao buscar arquivos do usuário") from e
    
    def _apply_filters(self, files: List, request: ListUserFilesInputDTO) -> List:
        """
        Aplica filtros de nome e tags aos arquivos.
        
        Args:
            files: Lista de arquivos para filtrar
            request: Parâmetros de filtro
            
        Returns:
            List: Lista de arquivos filtrados
        """
        filtered_files = []
        
        for file_entity in files:
            # Filtrar por nome (se especificado)
            if request.file_name and request.file_name.lower() not in file_entity.name.value.lower():
                continue
            
            # Filtrar por tags (se especificado)
            if request.tags:
                file_tags = [tag.value.lower() for tag in file_entity.tags]
                filter_tags = [tag.lower() for tag in request.tags]
                
                # Verificar se pelo menos uma tag de filtro está presente no arquivo
                if not any(filter_tag in file_tag for filter_tag in filter_tags for file_tag in file_tags):
                    continue
            
            filtered_files.append(file_entity)
        
        logger.debug(f"Após aplicar filtros: {len(filtered_files)} arquivos")
        return filtered_files
    
    def _apply_pagination(self, files: List, request: ListUserFilesInputDTO) -> dict:
        """
        Aplica paginação à lista de arquivos.
        
        Args:
            files: Lista de arquivos ordenados
            request: Parâmetros de paginação
            
        Returns:
            dict: Dicionário com arquivos paginados e metadados
        """
        total_count = len(files)
        start_index = (request.page - 1) * request.page_size
        end_index = start_index + request.page_size
        paginated_files = files[start_index:end_index]
        
        total_pages = (total_count + request.page_size - 1) // request.page_size
        
        return {
            'files': paginated_files,
            'total_count': total_count,
            'total_pages': total_pages
        }
    
    def _entity_to_dto(self, file_entity) -> FileResponseDTO:
        """
        Converte entidade de arquivo para DTO de resposta.
        
        Args:
            file_entity: Entidade de arquivo
            
        Returns:
            FileResponseDTO: DTO com dados do arquivo
            
        Raises:
            FileValidationException: Se houver erro na conversão
        """
        try:
            return entity_to_file_response_dto(file_entity)
        except Exception as e:
            logger.error(f"Erro ao converter arquivo para DTO: {str(e)}")
            raise FileValidationException("Erro ao processar dados do arquivo") from e