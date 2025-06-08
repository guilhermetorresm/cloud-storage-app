Para rodar o docker-compose front e back:

docker compose up --build -d

Para verificar se o container está rodando:

docker compose logs

Para parar o docker-compose:

docker compose down



Para rodar o build e levantar o servidor backend:
docker build -f Dockerfile.dev -t backend-image . && docker run -d --name backend-container -p 8080:8080 backend-image

Para rodar o build e levantar o servidor frontend:
docker build -f Dockerfiles/Dockerfile.dev -t frontend-image . && docker run -d --name frontend-container -p 8080:8080 frontend-image


Para parar o conteiner backend:

docker stop backend-container


# Para acessar o banco de dados do postgres pelo docker
docker exec -it postgres_db psql -U seu_usuario -d seu_banco