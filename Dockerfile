FROM python:3.6-alpine

RUN adduser -D service

WORKDIR /home/secretshare

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY SC_flask.py config.py models.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP SC_flask.py

RUN chown -R service:service ./
USER service

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]