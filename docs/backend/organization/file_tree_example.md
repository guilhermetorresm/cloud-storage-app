backend/
├── pyproject.toml                 # Gerenciamento de dependências com uv
├── requirements.txt               # Dependências geradas pelo uv
├── alembic.ini                   # Configuração do Alembic
├── docker-compose.yml            # Para desenvolvimento local
├── Dockerfile                    # Container da aplicação
├── .env.example                  # Exemplo de variáveis de ambiente
├── .gitignore
├── README.md
│
├── alembic/                      # Migrações do banco
│   ├── versions/
│   └── env.py
│
├── src/
│   └── cloud_storage/            # Nome do seu projeto
│       ├── __init__.py
│       │
│       ├── main.py               # Entry point da aplicação FastAPI
│       ├── config.py             # Configurações da aplicação
│       │
│       ├── shared/               # Código compartilhado entre camadas
│       │   ├── __init__.py
│       │   ├── exceptions.py     # Exceções customizadas
│       │   ├── constants.py      # Constantes da aplicação
│       │   └── utils.py          # Utilitários gerais
│       │
│       ├── domain/               # CAMADA DE DOMÍNIO (Clean Architecture)
│       │   ├── __init__.py
│       │   ├── entities/         # Entidades de domínio
│       │   │   ├── __init__.py
│       │   │   ├── user.py
│       │   │   ├── file.py
│       │   │   └── folder.py
│       │   │
│       │   ├── value_objects/    # Objetos de valor
│       │   │   ├── __init__.py
│       │   │   ├── email.py
│       │   │   ├── file_path.py
│       │   │   └── user_id.py
│       │   │
│       │   ├── repositories/     # Interfaces dos repositórios (abstrações)
│       │   │   ├── __init__.py
│       │   │   ├── user_repository.py
│       │   │   ├── file_repository.py
│       │   │   └── storage_repository.py
│       │   │
│       │   └── services/         # Serviços de domínio
│       │       ├── __init__.py
│       │       ├── file_ownership_service.py
│       │       └── file_validation_service.py
│       │
│       ├── application/          # CAMADA DE APLICAÇÃO (Casos de Uso)
│       │   ├── __init__.py
│       │   ├── dtos/            # Data Transfer Objects
│       │   │   ├── __init__.py
│       │   │   ├── user_dto.py
│       │   │   ├── file_dto.py
│       │   │   └── auth_dto.py
│       │   │
│       │   ├── use_cases/       # Casos de uso da aplicação
│       │   │   ├── __init__.py
│       │   │   ├── auth/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── login_use_case.py
│       │   │   │   ├── register_use_case.py
│       │   │   │   └── refresh_token_use_case.py
│       │   │   │
│       │   │   ├── files/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── upload_file_use_case.py
│       │   │   │   ├── download_file_use_case.py
│       │   │   │   ├── list_files_use_case.py
│       │   │   │   ├── delete_file_use_case.py
│       │   │   │   └── rename_file_use_case.py
│       │   │   │
│       │   │   └── users/
│       │   │       ├── __init__.py
│       │   │       ├── get_user_profile_use_case.py
│       │   │       └── update_user_profile_use_case.py
│       │   │
│       │   └── services/        # Serviços de aplicação (orquestração)
│       │       ├── __init__.py
│       │       ├── auth_service.py
│       │       ├── file_service.py
│       │       └── user_service.py
│       │
│       ├── infrastructure/       # CAMADA DE INFRAESTRUTURA
│       │   ├── __init__.py
│       │   ├── database/        # Configuração do banco de dados
│       │   │   ├── __init__.py
│       │   │   ├── connection.py
│       │   │   ├── models/      # Modelos SQLAlchemy
│       │   │   │   ├── __init__.py
│       │   │   │   ├── base.py
│       │   │   │   ├── user_model.py
│       │   │   │   ├── file_model.py
│       │   │   │   └── folder_model.py
│       │   │   │
│       │   │   └── repositories/ # Implementações dos repositórios
│       │   │       ├── __init__.py
│       │   │       ├── sqlalchemy_user_repository.py
│       │   │       ├── sqlalchemy_file_repository.py
│       │   │       └── s3_storage_repository.py
│       │   │
│       │   ├── auth/            # Infraestrutura de autenticação
│       │   │   ├── __init__.py
│       │   │   ├── oauth2_handler.py
│       │   │   ├── jwt_service.py
│       │   │   └── password_service.py
│       │   │
│       │   ├── storage/         # Integração com AWS S3
│       │   │   ├── __init__.py
│       │   │   ├── s3_client.py
│       │   │   └── s3_service.py
│       │   │
│       │   └── external/        # Serviços externos
│       │       ├── __init__.py
│       │       └── email_service.py
│       │
│       └── presentation/        # CAMADA DE APRESENTAÇÃO (API)
│           ├── __init__.py
│           ├── api/            # Controllers/Routers FastAPI
│           │   ├── __init__.py
│           │   ├── dependencies.py  # Dependências do FastAPI
│           │   ├── middleware.py    # Middlewares customizados
│           │   │
│           │   └── v1/         # Versão 1 da API
│           │       ├── __init__.py
│           │       ├── auth.py      # Endpoints de autenticação
│           │       ├── files.py     # Endpoints de arquivos
│           │       ├── users.py     # Endpoints de usuários
│           │       └── health.py    # Health check
│           │
│           ├── schemas/        # Pydantic schemas (request/response)
│           │   ├── __init__.py
│           │   ├── auth_schemas.py
│           │   ├── file_schemas.py
│           │   ├── user_schemas.py
│           │   └── common_schemas.py
│           │
│           └── middleware/     # Middlewares específicos
│               ├── __init__.py
│               ├── cors_middleware.py
│               ├── auth_middleware.py
│               └── error_handler.py
│
├── tests/                        # Testes da aplicação
│   ├── __init__.py
│   ├── conftest.py              # Configurações do pytest
│   ├── unit/                    # Testes unitários
│   │   ├── domain/
│   │   ├── application/
│   │   └── infrastructure/
│   │
│   ├── integration/             # Testes de integração
│   │   ├── api/
│   │   └── database/
│   │
│   └── e2e/                     # Testes end-to-end
│       └── test_file_operations.py
│
└── scripts/                     # Scripts utilitários
    ├── setup_dev.py
    ├── create_admin_user.py
    └── migrate_database.py