FROM python:3.10

WORKDIR /usr/src/app

COPY requirments.txt requirments.txt
RUN pip install -r requirements.txt


COPY src src/

ENTRYPOINT celery -A src.worker.app worker -l info
