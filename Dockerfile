FROM python:3.10-alpine
LABEL Author = SiteGroup5

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

RUN pip install --upgrade pip

RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual  \
    .tmp-build-deps gcc libc-dev python3-dev \
    linux-headers postgresql-dev  musl-dev \
    libffi-dev && pip install psycopg2

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D user
USER user

CMD gunicorn sfpm-backend.wsgi:application --bind 0.0.0.0:$PORT