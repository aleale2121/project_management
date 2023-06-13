FROM python:3.10 AS build


RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY ./requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt
FROM python:3.10

ENV PATH="/opt/venv/bin:$PATH"
COPY --from=build /opt/venv /opt/venv

WORKDIR /app
COPY ./app /app
COPY ./.env /app

EXPOSE 8000

RUN useradd -ms /bin/bash newuser
RUN chown -R newuser:newuser /app
USER newuser

CMD gunicorn app.wsgi:application --bind 0.0.0.0:8000
