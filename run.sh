	
docker run --name redis-server -d redis

uvicorn server:app --host 0.0.0.0 --port 8000

