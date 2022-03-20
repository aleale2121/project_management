FROM python:3.10-alpine

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev postgresql-client git \
        libpq-dev libc-dev linux-headers libffi-dev python3-dev

LABEL Author = SiteGroup5
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
RUN pip install psycopg2-binary

COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D user
USER user

CMD python manage.py runserver 0.0.0.0:$PORT