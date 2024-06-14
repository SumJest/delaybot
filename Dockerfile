FROM python:3.10-alpine as builder
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /usr/src/app
RUN pip install --upgrade pip

RUN apk update \
    && apk add gcc python3-dev

COPY ./src/requirements.txt ./
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

FROM python:3.10-alpine

RUN apk update \
    && apk add shadow

RUN mkdir -p /app

ENV HOME=/app
ENV APP_HOME=/app/delaybot

RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/logs

WORKDIR $APP_HOME

RUN apk update
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

ADD ./src $APP_HOME

RUN chmod +x /app/delaybot/entrypoint.sh

ENTRYPOINT ["/app/delaybot/entrypoint.sh"]