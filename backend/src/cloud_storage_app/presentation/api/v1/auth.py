"""
Endpoints de autenticação mockados para desenvolvimento
"""
from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from cloud_storage_app.presentation.schemas.user_schema import (
    UserCreate, 
    UserLogin, 
    UserResponse, 
    Token
)
from cloud_storage_app.shared.auth_utils import (
    get_password_hash,
    verify_password,
    create_access_token,
    generate_mock_user_id,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()

# Simulação de "banco de dados" em memória para desenvolvimento
# Em produção, isso seria substituído por um banco de dados real
mock_users_db: Dict[str, Dict[str, Any]] = {
    "admin": {
        "id": 1,
        "username": "admin",
        "email": "admin@exemplo.com",
        "first_name": "Admin",
        "last_name": "Sistema",
        "hashed_password": get_password_hash("admin123"),
        "is_active": True,
        "created_at": datetime.utcnow()
    },
    "usuario": {
        "id": 2,
        "username": "usuario",
        "email": "usuario@exemplo.com",
        "first_name": "Usuário",
        "last_name": "Teste",
        "hashed_password": get_password_hash("usuario123"),
        "is_active": True,
        "created_at": datetime.utcnow()
    }
}


def get_user_by_username(username: str) -> Dict[str, Any] | None:
    """Busca usuário por username no banco mockado"""
    return mock_users_db.get(username)


def get_user_by_email(email: str) -> Dict[str, Any] | None:
    """Busca usuário por email no banco mockado"""
    for user_data in mock_users_db.values():
        if user_data["email"] == email:
            return user_data
    return None


def create_user(user_data: UserCreate) -> Dict[str, Any]:
    """Cria um novo usuário no banco mockado"""
    new_user = {
        "id": generate_mock_user_id(),
        "username": user_data.username,
        "email": user_data.email,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "hashed_password": get_password_hash(user_data.password),
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    mock_users_db[user_data.username] = new_user
    return new_user


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Registrar um novo usuário no sistema
    
    Este é um endpoint mockado para desenvolvimento.
    Cria um novo usuário e retorna um token JWT válido.
    """
    # Verificar se usuário já existe
    if get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário com este nome de usuário já existe"
        )
    
    # Verificar se email já existe
    if get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário com este email já existe"
        )
    
    # Validar username
    if len(user_data.username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O nome de usuário deve ter pelo menos 3 caracteres"
        )
    
    # Validar senha
    if len(user_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha deve ter pelo menos 6 caracteres"
        )
    
    # Criar usuário
    try:
        new_user = create_user(user_data)
        
        # Criar token de acesso
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": new_user["username"], "user_id": new_user["id"]}, 
            expires_delta=access_token_expires
        )
        
        # Preparar resposta do usuário
        user_response = UserResponse(
            id=new_user["id"],
            username=new_user["username"],
            email=new_user["email"],
            first_name=new_user["first_name"],
            last_name=new_user["last_name"],
            is_active=new_user["is_active"],
            created_at=new_user["created_at"]
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # em segundos
            user=user_response
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """
    Fazer login no sistema
    
    Este é um endpoint mockado para desenvolvimento.
    Valida as credenciais e retorna um token JWT válido.
    
    Usuários de teste disponíveis:
    - admin / admin123
    - usuario / usuario123
    """
    # Buscar usuário
    user = get_user_by_username(user_credentials.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar senha
    if not verify_password(user_credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar se usuário está ativo
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo"
        )
    
    # Criar token de acesso
    try:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"], "user_id": user["id"]}, 
            expires_delta=access_token_expires
        )
        
        # Preparar resposta do usuário
        user_response = UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            is_active=user["is_active"],
            created_at=user["created_at"]
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # em segundos
            user=user_response
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user():
    """
    Obter informações do usuário atual
    
    Este endpoint mockado retorna sempre o usuário admin.
    Em produção, seria necessário validar o token JWT.
    """
    # Para demonstração, retorna sempre o usuário admin
    user = get_user_by_username("admin")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    return UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        is_active=user["is_active"],
        created_at=user["created_at"]
    )


@router.get("/users", response_model=list[UserResponse])
async def list_users():
    """
    Listar todos os usuários cadastrados (apenas para desenvolvimento)
    
    Este endpoint mostra todos os usuários do sistema mockado.
    """
    users = []
    for user_data in mock_users_db.values():
        users.append(UserResponse(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data["email"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            is_active=user_data["is_active"],
            created_at=user_data["created_at"]
        ))
    
    return users 