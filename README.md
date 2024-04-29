# pushNotificationServer

# Run Locally

uvicorn main:app --reload

# tests

python -m pytest

# docker commands

docker build -t fastapiapp .  
docker run -d --name mycontainer -p 80:80 fastapiapp  
docker run -d --network pushnotificationserver_network1 --name mycontainer -p 80:80 fastapiapp
docker stop mycontainer  
docker rm mycontainer

# docker compose commands

docker-compose -f docker-compose.yaml build
docker-compose -f docker-compose.yaml up -d
docker-compose -f docker-compose.yaml down
