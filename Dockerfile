FROM python:3.10-alpine
LABEL Author = SiteGroup5

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0
ENV DATABASE_URL postgres://hnipzlbgwdnqyz:24214279fcbfd416ba812ae79f6d27905038d15408b6889906e0ebf7cdccc7c4@ec2-54-226-18-238.compute-1.amazonaws.com:5432/d7hl55edumoqi3

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