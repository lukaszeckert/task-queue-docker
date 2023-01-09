import time

import click
from celery import Celery
# from docker_task_queue.common.rabbitmq_logger import RabbitMQLogger
# from docker_task_queue.common.settings import get_settings
# from docker_task_queue.common.tasks import RunInDocker

# settings = get_settings("environment")
# app = Celery(
#     "task-queue",
#     broker=f"pyamqp://{settings.user}:{settings.password}@"
#     f"{settings.rabbitmq_address}/",
#     backend="rpc://",
# )
# rabbit_logger = RabbitMQLogger(
#     user=settings.user,
#     password=settings.password,
#     exchange=settings.rabbitmq_logs_exchange,
#     rabbitmq_address=settings.rabbitmq_address,
# )
#
# task = RunInDocker(rabbit_logger)
# app.register_task(task)
#
# t = task.delay(image="ubuntu", entrypoint=["ls", "/"])
# rabbit_logger.bind(t.id)
# for key, message_count, line in rabbit_logger:
#     if line is not None:
#         print(line, end="")
#
#     if message_count == 0:
#         time.sleep(1)
#
# rabbit_logger.close_routing_key()
#
#
# t = task.delay(image="ubuntu32", entrypoint=["ls", "/"])
#
# rabbit_logger.bind(t.id)
# for key, message_count, line in rabbit_logger:
#     if line is not None:
#         print(line, end="")
#
#     if message_count == 0:
#         time.sleep(1)

@click.group()
def cli():
    pass
@cli.command
def cmd1():
    pass


@cli.command()
@click.option("--dockerfile",required=True, help="Dockerfile used when building project.")
@click.option("--docker_tag",required=True, help="Tag used for docker images when building")
@click.option("--docker_remote_repository", default=None, help="Docker repository to where to push images. When left blank, dtq will not push images.")
def init(dockerfile, docker_tag, docker_remote_repository):
    """can be used to initialize constant default cli values.
    This will create .dtq.ini file inside working directory."""
    pass

@cli.command()
def update():
    """Similar to init, but it will update existing values instead of overwriting them."""

if __name__ == '__main__':
    cli(obj={})