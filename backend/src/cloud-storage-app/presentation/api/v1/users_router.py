# app/api/v1/users_router.py
from fastapi import APIRouter, Depends
from app.schemas.user_schema import UserCreate, UserResponse
from app.application_services.user_service import UserService
# Importar dependências para obter o serviço (ex: get_user_service)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# A função get_user_service seria uma dependência que instancia o UserService
# com a sessão do banco de dados.
# def get_user_service(): ...

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user_endpoint(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service) # Injeção de dependência
):
    created_user = user_service.create_user(user_data)
    return created_user