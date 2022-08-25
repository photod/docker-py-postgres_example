# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY app.py .

EXPOSE 8000
VOLUME /var/lib/postgresql/data

ENTRYPOINT [ "python3", "app.py"]