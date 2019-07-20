FROM python:3.6-alpine3.7

ENV PYTHONUNBUFFERED=0

ENV DJANGO_SETTINGS_MODULE=dotacia.settings

RUN apk add --no-cache --virtual build-deps curl gcc g++ make postgresql-dev bash

RUN mkdir /dotacia

WORKDIR /dotacia

ADD . /dotacia

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
