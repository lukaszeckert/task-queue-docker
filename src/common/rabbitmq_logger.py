from typing import Optional, Tuple

import pika

CUSTOM_END_ROUTING_KEY_MESSAGE = "----TASK_QUEUE_DOCKER_END_OF_STREAM----"

class RabbitMQLogger:
    def __init__(self, rabbitmq_address: str, user: str, password: str, exchange: str):
        self.exchange = exchange
        self.queue_name = None  # Created after bind
        self.infinite = None

        self.connection = self._make_connection(rabbitmq_address, user, password)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=exchange, exchange_type="topic")

    def _make_connection(self, rabbitmq_address, user, password):
        credentials = pika.PlainCredentials(user, password)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(rabbitmq_address, credentials=credentials)
        )
        return connection

    def write(self, message: str, routing_key: Optional[str] = None):
        if routing_key is not None:
            self.channel.basic_publish(
                exchange=self.exchange, routing_key=routing_key, body=message.encode("utf-8")
            )

    def bind(self, routing_key: str = "", infinite = False):
        result = self.channel.queue_declare(queue="", exclusive=True)
        self.queue_name = result.method.queue
        self.infinite = infinite
        self.channel.queue_bind(
            queue=self.queue_name, exchange=self.exchange, routing_key=routing_key
        )

    def close_routing_key(self):
        self.channel.queue_unbind(queue=self.queue_name, exchange=self.exchange)
        self.queue_name = None

    def close(self):
        self.channel.close()
        self.connection.close()

    def read_one(self) -> Tuple[str, bytes]:
        if self.queue_name is None:
            raise ValueError("Bind needs to be called before read")

        routing_key, _, msg = self.channel.basic_get(self.queue_name)

        if msg:
            msg = msg.decode("utf-8")

        if routing_key:
            routing_key = routing_key.routing_key
        return routing_key, msg

    def send_end_stream_msg(self, routing_key):
        self.write(CUSTOM_END_ROUTING_KEY_MESSAGE, routing_key)

    def __iter__(self):
        return self

    def __next__(self):
        key, msg = self.read_one()
        if msg == CUSTOM_END_ROUTING_KEY_MESSAGE and not self.infinite:
            raise StopIteration()
        return key, msg

