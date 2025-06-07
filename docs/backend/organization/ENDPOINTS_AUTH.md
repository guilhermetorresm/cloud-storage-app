# Endpoints de Autenticação (Mockados)

Este documento descreve os endpoints de autenticação mockados criados para desenvolvimento e testes do frontend.

## Base URL
```
http://localhost:8000/auth
```

## Endpoints Disponíveis

### 1. Registro de Usuário
**POST** `/auth/register`

Registra um novo usuário no sistema.

**Body:**
```json
{
  "username": "novo_usuario",
  "email": "usuario@exemplo.com",
  "password": "senha123",
  "first_name": "Nome",
  "last_name": "Sobrenome"
}
```

**Resposta de Sucesso (201):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1234,
    "username": "novo_usuario",
    "email": "usuario@exemplo.com",
    "first_name": "Nome",
    "last_name": "Sobrenome",
    "is_active": true,
    "created_at": "2024-01-01T10:00:00.000000"
  }
}
```

### 2. Login
**POST** `/auth/login`

Faz login no sistema usando username e senha.

**Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Resposta de Sucesso (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@exemplo.com",
    "first_name": "Admin",
    "last_name": "Sistema",
    "is_active": true,
    "created_at": "2024-01-01T10:00:00.000000"
  }
}
```

### 3. Informações do Usuário Atual
**GET** `/auth/me`

Retorna informações do usuário atual (mockado - sempre retorna o admin).

**Resposta de Sucesso (200):**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@exemplo.com",
  "first_name": "Admin",
  "last_name": "Sistema",
  "is_active": true,
  "created_at": "2024-01-01T10:00:00.000000"
}
```

### 4. Listar Usuários
**GET** `/auth/users`

Lista todos os usuários cadastrados (apenas para desenvolvimento).

**Resposta de Sucesso (200):**
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@exemplo.com",
    "first_name": "Admin",
    "last_name": "Sistema",
    "is_active": true,
    "created_at": "2024-01-01T10:00:00.000000"
  },
  {
    "id": 2,
    "username": "usuario",
    "email": "usuario@exemplo.com",
    "first_name": "Usuário",
    "last_name": "Teste",
    "is_active": true,
    "created_at": "2024-01-01T10:00:00.000000"
  }
]
```

## Usuários de Teste Pré-cadastrados

Os seguintes usuários estão disponíveis para teste:

- **Username:** `admin` | **Senha:** `admin123`
- **Username:** `usuario` | **Senha:** `usuario123`

## Códigos de Erro

### 400 - Bad Request
- Username já existe
- Email já existe
- Username deve ter pelo menos 3 caracteres
- Senha deve ter pelo menos 6 caracteres

### 401 - Unauthorized
- Nome de usuário ou senha incorretos
- Usuário inativo

### 404 - Not Found
- Usuário não encontrado

### 500 - Internal Server Error
- Erro interno do servidor

## Como Usar o Token JWT

Após fazer login ou se registrar, você receberá um token JWT que deve ser incluído no header de autenticação das próximas requisições:

```
Authorization: Bearer <seu_token_aqui>
```

## Exemplo de Uso com cURL

### Registro:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "teste",
    "email": "teste@exemplo.com",
    "password": "teste123",
    "first_name": "Teste",
    "last_name": "Usuario"
  }'
```

### Login:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

### Usando o token:
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer <seu_token_aqui>"
```

## Observações Importantes

1. **Ambiente de Desenvolvimento:** Estes endpoints são mockados e usam um "banco de dados" em memória
2. **Dados Temporários:** Os dados são perdidos quando o servidor é reiniciado
3. **Segurança:** O SECRET_KEY está hardcoded - em produção, use variáveis de ambiente
4. **JWT Real:** Os tokens JWT são válidos e podem ser decodificados
5. **Expiração:** Os tokens expiram em 30 minutos por padrão 