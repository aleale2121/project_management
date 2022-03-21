FROM python:3.10-alpine
LABEL Author = SiteGroup5

RUN mkdir /app
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

RUN apk update \
    && apk add postgresql-dev gcc python3-dev \
    musl-dev postgresql-client git \
    libpq-dev libc-dev linux-headers \
    libffi-dev python3-dev



RUN pip install --upgrade pip
RUN pip install psycopg2

COPY ./requirements.txt /requirements.txt
RUN pip install -r ../requirements.txt

COPY ./app /app

RUN python manage.py collectstatic --noinput

RUN adduser -D user
USER user

CMD gunicorn app.wsgi:application --bind 0.0.0.0:$PORT