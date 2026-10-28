FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
RUN pip install --no-cache-dir --upgrade gunicorn

COPY server /app/server
COPY util /app/util
COPY gunicorn_conf.py /app
COPY ./nwac-stations.json /app

WORKDIR /app

EXPOSE 8080
CMD ["gunicorn", "--conf", "gunicorn_conf.py", "server.server:app"]
