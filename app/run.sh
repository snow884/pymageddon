	
docker run --name redis-server -it --rm -p 6379:6379 redis 

uvicorn server:app --host 0.0.0.0 --port 8000

python main.py