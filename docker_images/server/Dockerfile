# syntax=docker/dockerfile:1
FROM python:3.12

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip

ADD ./app/requirements.txt /app/requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r /app/requirements.txt

ADD ./app/ /app/

EXPOSE 80

ENV PYTHONPATH=/app/

WORKDIR "/app"

ENTRYPOINT [ "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "80"]
#ENTRYPOINT [ "gunicorn", "server:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:80"]
