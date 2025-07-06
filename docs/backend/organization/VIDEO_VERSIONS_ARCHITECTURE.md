# Arquitetura do Sistema de Versões de Vídeo

## Visão Geral

O sistema de versões de vídeo permite que um único vídeo tenha múltiplas versões em diferentes resoluções (480p, 720p, 1080p, 4K, etc.), otimizando a experiência do usuário baseada na qualidade de conexão e dispositivo.

## Componentes Principais

### 1. VideoVersion (Objeto de Valor)

```python
@dataclass(frozen=True)
class VideoVersion:
    resolution: str  # "480p", "720p", "1080p", "4K"
    file_path: FilePath
    is_original: bool = False
    processing_status: str = "pending"  # pending, processing, completed, failed
```

**Características:**
- **Imutável**: Garante consistência dos dados
- **Status de processamento**: Controla o ciclo de vida da versão
- **Identificação de original**: Distingue a versão do usuário das processadas

### 2. VideoFile (Entidade)

A entidade `VideoFile` foi estendida para gerenciar múltiplas versões:

```python
class VideoFile(BaseFile):
    _versions: Dict[str, VideoVersion] = field(default_factory=dict)
    _original_version: Optional[str] = None
```

## Estrutura de Caminhos no S3

O sistema usa uma estrutura hierárquica no S3:

```
bucket/
├── user_id/
│   └── videos/
│       └── YYYY/
│           └── MM/
│               └── DD/
│                   └── file_id/
│                       ├── 1080p/
│                       │   └── video.mp4
│                       ├── 720p/
│                       │   └── video.mp4
│                       ├── 480p/
│                       │   └── video.mp4
│                       └── 360p/
│                           └── video.mp4
```

**Exemplo de caminho:**
```
a5b1c3d4/videos/2025/01/15/f8e7d6c5/1080p/video.mp4
```

## Fluxo de Processamento

### 1. Upload Inicial
```python
video_file = VideoFile.create(
    owner_id=user_id,
    name="video.mp4",
    path="temp/upload/video.mp4",
    original_resolution="1080p"  # Versão original do usuário
)
```

### 2. Criação de Versões
```python
# Criar versão 720p
path_720p = FilePath.create_video(
    user_id=user_uuid,
    file_id=file_id,
    resolution="720p",
    file_name="video.mp4"
)

version_720p = VideoVersion(
    resolution="720p",
    file_path=path_720p,
    is_original=False,
    processing_status="pending"
)

video_file.add_version(version_720p)
```

### 3. Processamento Assíncrono
```python
# Marcar como em processamento
video_file.update_version_status("720p", "processing")

# Após processamento concluído
video_file.update_version_status("720p", "completed")
```

## Métodos Principais

### Gerenciamento de Versões
- `add_version(version)`: Adiciona nova versão
- `remove_version(resolution)`: Remove versão (exceto original)
- `get_version(resolution)`: Obtém versão específica
- `get_original_version()`: Obtém versão original

### Consultas
- `get_available_versions()`: Lista resoluções disponíveis
- `get_ready_versions()`: Versões prontas para uso
- `get_processing_versions()`: Versões em processamento
- `get_failed_versions()`: Versões que falharam

### Seleção Inteligente
- `get_best_available_version()`: Melhor versão disponível
- `get_best_available_version(max_resolution)`: Melhor versão com limite

## Status de Processamento

| Status | Descrição |
|--------|-----------|
| `pending` | Versão criada, aguardando processamento |
| `processing` | Versão sendo processada |
| `completed` | Versão pronta para uso |
| `failed` | Processamento falhou |

## Estratégias de Implementação

### 1. Processamento Assíncrono
```python
# Exemplo com Celery/RQ
@task
def process_video_versions(video_id: str, resolutions: List[str]):
    video = video_repository.get_by_id(video_id)
    
    for resolution in resolutions:
        # Marcar como processando
        video.update_version_status(resolution, "processing")
        video_repository.save(video)
        
        try:
            # Processar vídeo
            process_video_to_resolution(video, resolution)
            
            # Marcar como concluído
            video.update_version_status(resolution, "completed")
        except Exception as e:
            # Marcar como falhou
            video.update_version_status(resolution, "failed")
        
        video_repository.save(video)
```

### 2. Seleção Dinâmica
```python
def get_video_stream_url(video_id: str, user_connection: str) -> str:
    video = video_repository.get_by_id(video_id)
    
    # Determinar resolução baseada na conexão
    if user_connection == "slow":
        max_resolution = "480p"
    elif user_connection == "medium":
        max_resolution = "720p"
    else:
        max_resolution = "1080p"
    
    best_version = video.get_best_available_version(max_resolution)
    return generate_presigned_url(best_version.file_path)
```

### 3. Limpeza de Versões
```python
def cleanup_old_versions(video_id: str, keep_resolutions: List[str]):
    video = video_repository.get_by_id(video_id)
    
    for resolution in video.get_available_versions():
        if resolution not in keep_resolutions and resolution != video._original_version:
            # Deletar do S3
            delete_from_s3(video.get_version(resolution).file_path)
            # Remover da entidade
            video.remove_version(resolution)
    
    video_repository.save(video)
```

## Vantagens da Arquitetura

1. **Flexibilidade**: Suporte a qualquer resolução
2. **Escalabilidade**: Processamento assíncrono
3. **Consistência**: Controle de estado robusto
4. **Performance**: Seleção inteligente de versões
5. **Manutenibilidade**: Separação clara de responsabilidades

## Considerações de Implementação

### Storage
- **S3**: Estrutura hierárquica organizada
- **CDN**: Distribuição global das versões
- **Lifecycle**: Políticas de expiração por resolução

### Processamento
- **Queue**: Sistema de filas para processamento
- **Retry**: Mecanismo de retry para falhas
- **Monitoring**: Acompanhamento do progresso

### Performance
- **Caching**: Cache de metadados de versões
- **Lazy Loading**: Carregamento sob demanda
- **Compression**: Otimização de tamanho por resolução 