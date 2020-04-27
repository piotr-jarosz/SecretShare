FROM python:3.7-alpine

RUN adduser -D service

WORKDIR /home/service

COPY requirements.txt requirements.txt
RUN apk add linux-headers gcc libffi-dev openssl-dev musl-dev
RUN python -m venv venv
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY secretshare.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP secretshare.py

RUN chown -R service:service ./
USER service

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]