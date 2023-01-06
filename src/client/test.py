import time

import celery
from celery import Celery

from src.common.rabbitmq_logger import RabbitMQLogger
from src.common.settings import get_settings
from src.common.tasks import Add

settings = get_settings("environment")
app = Celery(
    "task-queue",
    broker=f"pyamqp://{settings.user}:{settings.password}@{settings.rabbitmq_address}/",
    backend="rpc://",
)
rabbit_logger = RabbitMQLogger(user=settings.user, password=settings.password, exchange=settings.rabbitmq_logs_exchange, rabbitmq_address=settings.rabbitmq_address)

task = Add(rabbit_logger)
app.register_task(task)

t = task.delay(image="ubuntu", entrypoint=["ls", "/"])
rabbit_logger.bind(t.id)
for key, line in rabbit_logger:
    if line is not None:
        print(line, end="")
    else:
        time.sleep(1)
rabbit_logger.close_routing_key()


t = task.delay(image="ubuntu32", entrypoint=["ls", "/"])

rabbit_logger.bind(t.id)
for key,line in rabbit_logger:
    if line is not None:
        print(line, end="")
    else:
        time.sleep(0.1)
