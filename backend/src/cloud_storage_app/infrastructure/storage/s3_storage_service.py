import logging
from typing import IO, Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError
from dependency_injector.wiring import inject, Provide

from cloud_storage_app.domain.services.storage_service import IStorageService
from cloud_storage_app.domain.value_objects import FilePath
from cloud_storage_app.config import StorageSettings

logger = logging.getLogger(__name__)

class S3StorageService(IStorageService):
    """
    Implementação concreta do serviço de armazenamento usando AWS S3.
    """

    @inject
    def __init__(self, storage_settings: StorageSettings = Provide["storage_settings"]):
        self._settings = storage_settings
        self._s3_client = boto3.client(
            "s3",
            aws_access_key_id=self._settings.aws_access_key_id,
            aws_secret_access_key=self._settings.aws_secret_access_key,
            region_name=self._settings.aws_region,
            endpoint_url=self._settings.s3_endpoint_url  # Útil para testes locais com MinIO
        )
        self._bucket_name = self._settings.s3_bucket_name
        logger.info(f"S3StorageService inicializado para o bucket: {self._bucket_name}")

    async def upload_file(self, file_object: IO[Any], file_path: FilePath, mime_type: str) -> None:
        """Faz o upload de um arquivo para o bucket S3."""
        try:
            self._s3_client.upload_fileobj(
                file_object,
                self._bucket_name,
                str(file_path),
                ExtraArgs={'ContentType': mime_type}
            )
            logger.info(f"Arquivo enviado com sucesso para S3: {file_path}")
        except ClientError as e:
            logger.error(f"Erro ao fazer upload para o S3: {e}")
            raise ConnectionError(f"Falha no upload do arquivo: {file_path}") from e

    async def delete_file(self, file_path: FilePath) -> None:
        """Deleta um arquivo do bucket S3."""
        try:
            self._s3_client.delete_object(Bucket=self._bucket_name, Key=str(file_path))
            logger.info(f"Arquivo deletado com sucesso do S3: {file_path}")
        except ClientError as e:
            logger.error(f"Erro ao deletar arquivo do S3: {e}")
            raise ConnectionError(f"Falha ao deletar o arquivo: {file_path}") from e

    async def get_presigned_url(self, file_path: FilePath, expiration: int = 3600) -> Optional[str]:
        """Gera uma URL pré-assinada para download."""
        try:
            response = self._s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self._bucket_name, 'Key': str(file_path)},
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            logger.error(f"Erro ao gerar URL pré-assinada: {e}")
            return None

    async def file_exists(self, file_path: FilePath) -> bool:
        """Verifica se um arquivo existe no bucket S3."""
        try:
            self._s3_client.head_object(Bucket=self._bucket_name, Key=str(file_path))
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logger.error(f"Erro ao verificar existência do arquivo no S3: {e}")
                raise ConnectionError(f"Não foi possível verificar o arquivo: {file_path}") from e
