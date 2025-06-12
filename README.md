# Cloud Storage App

<div align="center">
  <h3>🗂️ Aplicação Completa de Armazenamento em Nuvem</h3>
  <p>Sistema moderno de upload e gerenciamento de arquivos com backend FastAPI e frontend React</p>
  
  ![Python](https://img.shields.io/badge/Python-3.11-blue)
  ![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-green)
  ![React](https://img.shields.io/badge/React-19.1.0-blue)
  ![AWS](https://img.shields.io/badge/AWS-S3-orange)
  ![Docker](https://img.shields.io/badge/Docker-Enabled-blue)
</div>

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Configuração](#instalação-e-configuração)
- [Como Executar](#como-executar)
- [API Documentation](#api-documentation)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Deploy AWS](#deploy-aws)
- [Testes](#testes)
- [Contribuição](#contribuição)
- [Licença](#licença)

## 🎯 Sobre o Projeto

O **Cloud Storage App** é uma aplicação completa de armazenamento em nuvem que permite aos usuários fazer upload, organizar e gerenciar seus arquivos de forma segura. O sistema oferece autenticação robusta, interface moderna e integração com AWS S3 para armazenamento escalável.

### ✨ Funcionalidades Principais

- 🔐 **Autenticação Segura** - Sistema de login/registro com JWT
- 📤 **Upload de Arquivos** - Suporte a múltiplos tipos de arquivo
- 📱 **Interface Responsiva** - Design moderno e adaptável
- ☁️ **Armazenamento AWS S3** - Escalabilidade e confiabilidade

## 🛠️ Tecnologias Utilizadas

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** - Framework web moderno e rápido
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - ORM para banco de dados
- **[Alembic](https://alembic.sqlalchemy.org/)** - Migrações de banco
- **[Pydantic](https://pydantic.dev/)** - Validação de dados
- **[JWT](https://jwt.io/)** - Autenticação stateless
- **[Boto3](https://boto3.amazonaws.com/)** - SDK da AWS
- **[PostgreSQL](https://www.postgresql.org/)** - Banco de dados

### Frontend
- **[React](https://react.dev/)** - Biblioteca para interfaces
- **[Tailwind CSS](https://tailwindcss.com/)** - Framework CSS utilitário
- **[Axios](https://axios-http.com/)** - Cliente HTTP
- **[React Router](https://reactrouter.com/)** - Roteamento
- **[Lucide React](https://lucide.dev/)** - Ícones modernos

### DevOps & Infraestrutura
- **[Docker](https://www.docker.com/)** - Containerização
- **[Docker Compose](https://docs.docker.com/compose/)** - Orquestração local
- **[AWS S3](https://aws.amazon.com/s3/)** - Armazenamento de arquivos

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Frontend      │◄──►│   Backend       │◄──►│   AWS S3        │
│   (React)       │    │   (FastAPI)     │    │   (Storage)     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │                 │
                       │   PostgreSQL    │
                       │   (Database)    │
                       │                 │
                       └─────────────────┘
```

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter as seguintes ferramentas instaladas:

- **[Python 3.11+](https://www.python.org/downloads/)**
- **[Node.js 16+](https://nodejs.org/)**
- **[Docker](https://www.docker.com/get-started)**
- **[Docker Compose](https://docs.docker.com/compose/install/)**
- **[Git](https://git-scm.com/)**

### Contas Necessárias
- **[AWS Account](https://aws.amazon.com/)** - Para S3 bucket
- **PostgreSQL** - Banco local ou remoto

## ⚙️ Instalação e Configuração

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/cloud-storage-app.git
cd cloud-storage-app
```

### 2. Configuração do Backend

```bash
# Entre na pasta do backend
cd backend

# Instale o uv (gerenciador de pacotes Python)
pip install uv

# Instale as dependências
uv sync

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

### 3. Configuração do Frontend

```bash
# Entre na pasta do frontend
cd frontend

# Instale as dependências
npm install

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com a URL da API
```

## 🚀 Como Executar

### Opção 1: Com Docker (Recomendado)

```bash
# Execute todo o stack com Docker Compose
# Acesse uma das pastas frontend/backend

# Execute o comando do docker para cada pasta
docker-compose up --build -d

# Acompanhe os logs
docker-compose logs -f
```

A aplicação estará disponível em:
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs

### Opção 2: Desenvolvimento Local

#### Backend
```bash
cd backend

# Execute as migrações
uv run alembic upgrade head

# Inicie o servidor de desenvolvimento
uv run uvicorn src.cloud_storage_app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend

# Inicie o servidor de desenvolvimento
npm start
```

## 📚 API Documentation

A documentação interativa da API está disponível em:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Principais Endpoints

```http
POST /auth/register     # Registro de usuário
POST /auth/login        # Login

POST /files/upload     # Upload de arquivo
GET  /files/          # Lista arquivos do usuário
GET  /files/{id}      # Download de arquivo
DELETE /files/{id}    # Deletar arquivo

```

## 📁 Estrutura do Projeto

```
cloud-storage-app/
├── backend/                 # API FastAPI
│   ├── src/
│   │   └── cloud_storage_app/
│   │       ├── main.py     # Entry point
│   │       ├── auth/       # Autenticação
│   │       ├── files/      # Gerenciamento de arquivos
│   │       ├── database/   # Configuração DB
│   │       └── aws/        # Integração AWS
│   ├── alembic/            # Migrações
│   ├── tests/              # Testes
│   ├── Dockerfiles/        # Dockerfiles
│   └── pyproject.toml      # Dependências Python
├── frontend/               # App React
│   ├── src/
│   │   ├── components/     # Componentes React
│   │   ├── pages/          # Páginas
│   │   ├── services/       # API calls
│   │   └── hooks/          # React hooks
│   ├── public/             # Assets estáticos
│   └── package.json        # Dependências Node
├── docs/                   # Documentação
└── docker-compose.yml      # Orquestração
```

## 🔐 Variáveis de Ambiente

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/cloud_storage

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_BUCKET_NAME=your-bucket-name
AWS_REGION=us-east-1

# API
API_V1_STR=/api/v1
PROJECT_NAME="Cloud Storage API"
```

### Frontend (.env)
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_VERSION=v1
```

## ☁️ Deploy AWS

### Configuração do S3 Bucket

1. **Crie um bucket S3**:
```bash
aws s3 mb s3://seu-bucket-name
```

2. **Configure CORS**:
```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": []
    }
]
```

3. **Configure IAM Policy**:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::seu-bucket-name/*"
        }
    ]
}
```

## 🧪 Testes

### Backend
```bash
cd backend

# Execute todos os testes
uv run pytest

# Execute com coverage
uv run pytest --cov=src

# Execute testes específicos
uv run pytest tests/test_auth.py
```

### Frontend
```bash
cd frontend

# Execute os testes
npm test

# Execute com coverage
npm run test:coverage
```

## 🤝 Contribuição

Contribuições são sempre bem-vindas! Para contribuir:

1. **Fork** o projeto
2. Crie uma **branch** para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. Abra um **Pull Request**

### Diretrizes de Contribuição

- Siga os padrões de código estabelecidos
- Adicione testes para novas funcionalidades
- Atualize a documentação quando necessário
- Use conventional commits

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<div align="center">
  <p><strong>Desenvolvido por:</strong></p>

  <p><strong>Felipe Holanda Aguiar de Carvalho</strong><br>
    <a href="mailto:felipehac@ufpi.edu.br">📧 Email</a> •
    <a href="https://github.com/WhityWolf">🐙 GitHub</a> •
    <a href="https://www.linkedin.com/in/felipe-carvalho-67b0752a8/">💼 LinkedIn</a>
  </p>

  <p><strong>Guilherme Torres Melo</strong><br>
    <a href="mailto:guilhermetorresm@ufpi.edu.br">📧 Email</a> •
    <a href="https://github.com/guilhermetorresm">🐙 GitHub</a> 
  </p>

  <p><strong>Jordana Bezerra França</strong><br>
    <a href="mailto:jordanafranca@ufpi.edu.br">📧 Email</a> •
    <a href="https://github.com/jordanabfranca">🐙 GitHub</a> •
    <a href="https://www.linkedin.com/in/jordana-bezerra/">💼 LinkedIn</a>
  </p>

  <p><strong>Nivaldo Nogueira Paranaguá Santos e Silva</strong><br>
    <a href="mailto:nivaldonogueira2001@ufpi.edu.br">📧 Email</a> •
    <a href="https://github.com/Naparanagua">🐙 GitHub</a> •
    <a href="https://www.linkedin.com/in/nivaldo-nogueira/">💼 LinkedIn</a>
  </p>
</div>

