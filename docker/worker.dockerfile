FROM python:3.10

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt
#RUN pip install -r requirements.txt


COPY docker_task_queue src/

ENTRYPOINT celery -A src.worker.app worker -l info
