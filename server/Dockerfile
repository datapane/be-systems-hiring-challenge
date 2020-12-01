#server
FROM python:3.7.1-slim

RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  gcc

WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY main.py /app/main.py

