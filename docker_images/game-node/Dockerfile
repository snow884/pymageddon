FROM python:3.12

RUN pip install --upgrade pip

ADD ./app/requirements.txt /app/requirements.txt

RUN pip install --upgrade setuptools

RUN pip3 install -r /app/requirements.txt

ADD  ./app/ /app/

EXPOSE 5000

ENV PYTHONPATH=/app/    

WORKDIR "/app"

RUN python setup.py build_ext --inplace

ENTRYPOINT [ "python","run.py"]

