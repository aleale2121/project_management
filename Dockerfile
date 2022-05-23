FROM python:3.10-alpine AS build-python
RUN apk update && apk add --virtual build-essential gcc python3-dev musl-dev postgresql-dev \ 
    git libffi-dev libpq-dev libc-dev linux-headers
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY ./requirements.txt /requirements.txt
RUN pip install -r ./requirements.txt


FROM python:3.10-alpine
LABEL Author = SiteGroup5


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

ENV PATH="/opt/venv/bin:$PATH"
COPY --from=build-python /opt/venv /opt/venv
RUN apk update \
    && apk add --virtual build-deps postgresql-dev gcc python3-dev \
    musl-dev postgresql-client git \
    libpq-dev libc-dev linux-headers \
    libffi-dev python3-dev



RUN pip install --upgrade pip
RUN pip install psycopg2-binary

RUN mkdir /app
WORKDIR /app
# COPY ./requirements.txt /requirements.txt
# RUN pip install -r ../requirements.txt

COPY ./app /app

RUN python manage.py collectstatic --noinput

RUN adduser -D user
USER user

CMD gunicorn app.wsgi:application --bind 0.0.0.0:$PORT
