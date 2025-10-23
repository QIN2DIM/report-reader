if [ -f .env ]; then
    cp .env app/
else
    echo ".env 文件不存在，创建空文件"
    touch .env
    cp .env app/
fi

docker compose down
docker compose up -d
docker compose logs -f
