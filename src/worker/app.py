import time
from typing import Optional


from src.worker.rabbitmq_logger import RabbitMQLogger
from src.worker.settings import _env

from celery import Celery
import os


settings = _env()

rabbit_logger = RabbitMQLogger(user=settings.user, password=settings.password, exchange=settings.rabbitmq_logs_exchange, rabbitmq_address=settings.rabbitmq_address)
app = Celery('app', broker=f'pyamqp://{settings.user}:{settings.password}@{settings.rabbitmq_address}//')



@app.task(task_reject_on_worker_lost=True, acks_late=True)
def add(x, y, routing_key: Optional[str] = None):
    rabbit_logger.write(b"Started processing", routing_key)
    res = x + y
    rabbit_logger.write(f"End of processing, result is: {res}")
    return res



#
#
# import pika
# credentials = pika.PlainCredentials('taskqueuedocker', 'CHANGE_ME')
#
# connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',credentials=credentials))
# channel = connection.channel()
# result = channel.queue_declare(queue='', exclusive=True)
# # channel.exchange_declare(exchange='logs', exchange_type='fanout')
# channel.queue_bind(exchange='logs',
#                    queue=result.method.queue)
#
# channel.basic_publish(exchange=result.method.queue, routing_key='', body=b"TEST")
#
#
#
# channel.exchange_declare(exchange='logs', exchange_type='fanout')
#
# result = channel.queue_declare(queue='', exclusive=True)
# queue_name = result.method.queue
#
# channel.queue_bind(exchange='logs', queue=queue_name)
#
# print(' [*] Waiting for logs. To exit press CTRL+C')
#
# def callback(ch, method, properties, body):
#     print(" [x] %r" % body)
#
# channel.basic_consume(
#     queue=queue_name, on_message_callback=callback, auto_ack=True)
#
# channel.start_consuming()
