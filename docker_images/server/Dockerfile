FROM python:3.10

RUN pip install --upgrade pip

ADD ./requirements.txt /app/requirements.txt

RUN pip3 install -r /app/requirements.txt

ADD  ../../app/ /app/

EXPOSE 5000

ENV PYTHONPATH=/app/

WORKDIR "/app"
uvicorn server:app --reload
ENTRYPOINT [ "uvicorn","server:app", "--reload"]

