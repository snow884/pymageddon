FROM python:3.12

RUN pip install --upgrade pip

ADD ./app/requirements.txt /app/requirements.txt

RUN pip3 install -r /app/requirements.txt

ADD  ../../app/ /app/

EXPOSE 80

ENV PYTHONPATH=/app/

WORKDIR "/app"

#ENTRYPOINT [ "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "80"]
ENTRYPOINT [ "gunicorn", "server:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:80"]
