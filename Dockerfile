FROM python:3.9-slim

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY app .

CMD gunicorn app:app --bind 0.0.0.0:8000