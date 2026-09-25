# syntax=docker/dockerfile:1
FROM python:3.12

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools

ADD ./app/requirements.txt /app/requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r /app/requirements.txt

ADD  ./app/ /app/

EXPOSE 5000

ENV PYTHONPATH=/app/    

WORKDIR "/app"

RUN python setup.py build_ext --inplace

ENTRYPOINT [ "python","run.py"]

