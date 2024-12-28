	
docker run --name redis-server -it --rm redis 

uvicorn server:app --host 0.0.0.0 --port 8000

