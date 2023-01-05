from typing import Optional

import pika


class RabbitMQLogger:

    def __init__(self, rabbitmq_address: str, user: str, password: str, exchange: str):
        self.exchange = exchange
        self.queue_name = None # Created after bind

        self.connection = self._make_connection(rabbitmq_address, user, password)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=exchange, exchange_type="direct")


    def _make_connection(self, rabbitmq_address, user, password):
        credentials = pika.PlainCredentials(user, password)
        connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_address, credentials=credentials))
        return connection

    def write(self, message: bytes, routing_key: Optional[str] = None):
        if routing_key is not None:
            self.channel.basic_publish(exchange=self.exchange, routing_key=routing_key, body=message)

    def bind(self, routing_key: str = ""):
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.queue_name = result.method.queue

        self.channel.queue_bind(queue=self.queue_name, exchange=self.exchange, routing_key=routing_key)

    def close_routing_key(self):
        self.channel.queue_unbind(queue=self.queue_name, exchange=self.exchange)
        self.queue_name = None


    def close(self):
        self.channel.close()
        self.connection.close()

    def read_one(self) -> bytes:
        if self.queue_name is None:
            raise ValueError("Bind needs to be called before read")

        _, _, msg = self.channel.basic_get(self.queue_name)
        return msg

    def __enter__(self):
        if self.queue_name is None:
            ValueError("Cannot enter without bind. Use 'with var.bind(...):'")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()