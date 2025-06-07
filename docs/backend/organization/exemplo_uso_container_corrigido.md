# ==========================================
# EXEMPLO DE USO DO CONTAINER CORRIGIDO
# ==========================================

from fastapi import APIRouter, HTTPException, Depends
from dependency_injector.wiring import inject, Provide
from sqlalchemy.ext.asyncio import AsyncSession

from cloud_storage_app.infrastructure.di.container import (
    Container,
    get_database_session,
    get_user_repository,
    get_password_application_service,
    get_settings_from_container
)
from cloud_storage_app.infrastructure.database.repositories.user_repository import UserRepository
from cloud_storage_app.application.services.password_service import PasswordApplicationService
from cloud_storage_app.config import Settings

router = APIRouter()

# ==========================================
# EXEMPLO 1: USANDO INJEÇÃO DIRETA COM SESSÃO
# ==========================================

@router.post("/users")
@inject
async def create_user(
    user_data: dict,
    # Serviços via container (sem sessão)
    password_service: PasswordApplicationService = Provide[Container.password_application_service],
    settings: Settings = Provide[Container.settings],
    # Sessão via Depends
    db: AsyncSession = Depends(get_database_session)
):
    """
    Exemplo corrigido - mistura injeção do container com Depends para sessão.
    """
    try:
        # Criar repository manualmente com a sessão
        user_repo = UserRepository(session=db)
        
        # Usar serviços injetados
        hashed_password = await password_service.hash_password(user_data["password"])
        
        # Criar usuário
        user = await user_repo.create({
            **user_data,
            "password": hashed_password
        })
        
        return {"id": user.id, "email": user.email}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==========================================
# EXEMPLO 2: USANDO APENAS DEPENDS (MAIS SIMPLES)
# ==========================================

@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    # Tudo via Depends - mais consistente
    db: AsyncSession = Depends(get_database_session),
    password_service: PasswordApplicationService = Depends(lambda: get_container().password_application_service()),
    settings: Settings = Depends(lambda: get_container().settings())
):
    """
    Exemplo usando apenas Depends - mais consistente e simples.
    """
    user_repo = UserRepository(session=db)
    
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "email": user.email,
        "environment": settings.app.environment
    }


# ==========================================
# EXEMPLO 3: VERSÃO HÍBRIDA (RECOMENDADA)
# ==========================================

def get_user_repo_with_session(db: AsyncSession = Depends(get_database_session)):
    """Helper para criar repositório com sessão"""
    return UserRepository(session=db)

@router.put("/users/{user_id}/password")
@inject
async def change_password(
    user_id: int,
    new_password: str,
    # Repository com sessão via helper
    user_repo: UserRepository = Depends(get_user_repo_with_session),
    # Serviços via container
    password_service: PasswordApplicationService = Provide[Container.password_application_service]
):
    """
    Versão híbrida - melhor dos dois mundos.
    """
    # Buscar usuário
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Hash da nova senha
    hashed_password = await password_service.hash_password(new_password)
    
    # Atualizar usuário
    await user_repo.update(user_id, {"password": hashed_password})
    
    return {"message": "Password updated successfully"}


# ==========================================
# HELPERS PARA REPOSITÓRIOS (RECOMENDADO)
# ==========================================

def get_user_repository_with_db(db: AsyncSession = Depends(get_database_session)):
    """Factory para UserRepository com sessão injetada"""
    return UserRepository(session=db)

# Use esta nos seus endpoints:
# user_repo: UserRepository = Depends(get_user_repository_with_db)


# ==========================================
# VERSÃO FINAL RECOMENDADA
# ==========================================

@router.post("/users/final")
async def create_user_final(
    user_data: dict,
    # Use helpers para repositórios
    user_repo: UserRepository = Depends(get_user_repository_with_db),
    # Use lambda para serviços do container
    password_service: PasswordApplicationService = Depends(lambda: get_container().password_application_service())
):
    """
    Versão final recomendada - simples e consistente.
    """
    hashed_password = await password_service.hash_password(user_data["password"])
    
    user = await user_repo.create({
        **user_data,
        "password": hashed_password
    })
    
    return {"id": user.id, "email": user.email}


# ==========================================
# RESUMO DAS CORREÇÕES:
# ==========================================

"""
❌ PROBLEMA ORIGINAL:
- dependency-injector não tem init_resources() assíncrono
- providers.Resource para sessão estava complicando

✅ SOLUÇÃO:
- Usar container.init_resources() síncrono
- Sessões via Depends(get_database_session)
- Repositórios criados manualmente com sessão
- Serviços via container ou lambda functions

🎯 PADRÕES RECOMENDADOS:

1. Para repositórios: Depends(get_repository_with_db)
2. Para serviços: Depends(lambda: get_container().servico())
3. Para sessões: Depends(get_database_session)

🚀 RESULTADO:
- Container mais simples e estável
- Menos mágica, mais explícito
- Fácil de entender e debugar
- Compatível com dependency-injector
""" 