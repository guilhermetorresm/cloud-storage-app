Para rodar o docker-compose:

docker compose up --build -d

Para verificar se o container está rodando:

docker compose logs

Para parar o docker-compose:

docker compose down



Para rodar o build e levantar o servidor backend:

docker build -f Dockerfile.dev -t backend-image . && docker run -d --name backend-container -p 8080:8080 backend-image

Para parar o conteiner backend:

docker stop backend-container
