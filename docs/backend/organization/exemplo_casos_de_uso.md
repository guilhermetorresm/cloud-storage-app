# ==========================================
# MELHORES PRÁTICAS: CASOS DE USO NO CONTAINER
# ==========================================

from fastapi import APIRouter, HTTPException, Depends
from dependency_injector.wiring import inject, Provide
from sqlalchemy.ext.asyncio import AsyncSession

from cloud_storage_app.infrastructure.di.container import (
    Container,
    get_database_session,
    get_create_user_use_case
)
from cloud_storage_app.application.use_cases.user.create_user_use_case import CreateUserUseCase

router = APIRouter()

# ==========================================
# ✅ MELHOR PRÁTICA: USANDO CASOS DE USO
# ==========================================

@router.post("/users")
@inject
async def create_user_endpoint(
    user_data: dict,
    # 🎯 Caso de uso injetado via container
    create_user_use_case: CreateUserUseCase = Provide[Container.create_user_use_case],
    # 🎯 Sessão injetada via Depends para passar ao caso de uso
    db: AsyncSession = Depends(get_database_session)
):
    """
    ✅ PADRÃO RECOMENDADO:
    - Endpoint só coordena entrada/saída
    - Caso de uso implementa regra de negócio
    - Dependências claras e testáveis
    """
    try:
        # Caso de uso recebe a sessão que precisa
        user = await create_user_use_case.execute(
            user_data=user_data,
            db_session=db  # providers.Dependency() espera esta sessão
        )
        
        return {
            "id": user.id,
            "email": user.email,
            "message": "User created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==========================================
# 🏗️ COMO SERIA O CASO DE USO (EXEMPLO)
# ==========================================

"""
# application/use_cases/user/create_user_use_case.py

class CreateUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
        db_session: AsyncSession = None  # Será injetada pelo endpoint
    ):
        self.user_repository = user_repository
        self.password_service = password_service
        self.db_session = db_session
    
    async def execute(self, user_data: dict, db_session: AsyncSession) -> User:
        # Injetar a sessão nos repositórios que precisam
        self.user_repository.session = db_session
        
        # Regras de negócio aqui
        if await self.user_repository.exists_by_email(user_data["email"]):
            raise ValueError("Email já está em uso")
        
        # Hash da senha
        hashed_password = await self.password_service.hash_password(
            user_data["password"]
        )
        
        # Criar usuário
        user = await self.user_repository.create({
            **user_data,
            "password": hashed_password
        })
        
        # Commit da transação
        await db_session.commit()
        
        return user
"""

# ==========================================
# 🎯 VANTAGENS DOS CASOS DE USO NO CONTAINER:
# ==========================================

"""
✅ ORGANIZAÇÃO CLEAN ARCHITECTURE:
├── Presentation (Endpoints)
│   └── Coordena entrada/saída
├── Application (Casos de Uso) ← AQUI
│   └── Implementa regras de negócio
├── Domain (Entidades/Value Objects)
│   └── Modelos de negócio
└── Infrastructure (Repos/Services)
    └── Implementações técnicas

✅ BENEFÍCIOS:

1. 🧪 TESTABILIDADE:
   - Mock fácil dos casos de uso
   - Testes unitários isolados
   - Injeção de dependências clara

2. 🔄 REUTILIZAÇÃO:
   - Casos de uso podem ser usados em múltiplos endpoints
   - CLI, Workers, GraphQL podem usar os mesmos casos de uso
   - Lógica de negócio centralizada

3. 📝 MANUTENIBILIDADE:
   - Separação clara de responsabilidades
   - Endpoints magros, casos de uso gordos
   - Fácil evolução das regras de negócio

4. 🏗️ ESCALABILIDADE:
   - Adicionar novos casos de uso é simples
   - Container gerencia automaticamente as dependências
   - Padrão consistente em toda aplicação

✅ QUANDO USAR providers.Dependency():

1. 🗄️ SESSÕES DE BANCO:
   - Vêm do endpoint (lifecycle da request)
   - Não podem ser singleton
   - Precisam ser injetadas externamente

2. 🔐 CONTEXTO DO USUÁRIO:
   - User ID, permissions, etc.
   - Específicos da request
   - Vêm de middleware/JWT

3. 📝 REQUEST DATA:
   - Dados específicos da operação
   - Não faz sentido estar no container
   - Passados pelos endpoints

✅ ESTRUTURA RECOMENDADA NO CONTAINER:

# Infraestrutura (Singleton)
database_manager = providers.Singleton(DatabaseManager)
password_service = providers.Singleton(PasswordService)

# Repositórios (Factory + Dependency)
user_repository = providers.Factory(
    UserRepository,
    session=providers.Dependency()  # Vem do endpoint
)

# Casos de Uso (Factory + Dependencies)
create_user_use_case = providers.Factory(
    CreateUserUseCase,
    user_repository=user_repository,     # Vem do container
    password_service=password_service,   # Vem do container
    db_session=providers.Dependency()    # Vem do endpoint
)

🎯 RESULTADO:
- Código mais limpo e organizado
- Regras de negócio centralizadas
- Fácil manutenção e evolução
- Testes mais simples
- Padrão escalável
"""

# ==========================================
# 📖 EXEMPLO ADICIONAL: MÚLTIPLOS CASOS DE USO
# ==========================================

# No container você poderia ter:
"""
# Casos de uso de usuário
create_user_use_case = providers.Factory(CreateUserUseCase, ...)
update_user_use_case = providers.Factory(UpdateUserUseCase, ...)
delete_user_use_case = providers.Factory(DeleteUserUseCase, ...)
get_user_use_case = providers.Factory(GetUserUseCase, ...)

# Casos de uso de autenticação
login_use_case = providers.Factory(LoginUseCase, ...)
refresh_token_use_case = providers.Factory(RefreshTokenUseCase, ...)

# Casos de uso de arquivos
upload_file_use_case = providers.Factory(UploadFileUseCase, ...)
delete_file_use_case = providers.Factory(DeleteFileUseCase, ...)
""" 