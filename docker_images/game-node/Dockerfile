FROM python:3.12

RUN pip install --upgrade pip

ADD ./app/requirements.txt /app/requirements.txt

RUN pip3 install -r /app/requirements.txt

ADD  ./app/ /app/

RUN python /app/setup.py build_ext --inplace

EXPOSE 5000

ENV PYTHONPATH=/app/    

WORKDIR "/app"

ENTRYPOINT [ "python","run.py"]

