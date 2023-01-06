import time
from typing import List, Optional, Union

from celery import Task

import docker
from docker.errors import DockerException

from src.common.rabbitmq_logger import RabbitMQLogger


class Add(Task):
    def __init__(self, rabbitmq_logger: Optional[RabbitMQLogger] = None):
        self.rabbitmq_logger = rabbitmq_logger
        self.acks_late = True
        self.reject_on_worker_lost = True

        self.docker_client = docker.from_env()


    def run(
        self,
        image: str,
        entrypoint: Optional[Union[str, List[str]]] = None,
        mounts: Optional[List[str]] = None,

    ):
        try:
            self.container = self.docker_client.containers.run(image=image, entrypoint=entrypoint, mounts=mounts, detach=True)

            for line in self.container.logs(stream=True):
                if self.rabbitmq_logger:
                    self.rabbitmq_logger.write(line.decode("utf-8"), self.request.id)
        except DockerException as e:
            self.rabbitmq_logger.write(str(e), self.request.id)
        finally:
            self.container = None
            self.rabbitmq_logger.send_end_stream_msg(self.request.id)

        return None

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if self.container:
            self.container.kill()
            self.container = None


