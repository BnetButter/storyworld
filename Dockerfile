FROM python:3.10-slim
RUN apt-get update
RUN apt-get install -y gcc
WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt
