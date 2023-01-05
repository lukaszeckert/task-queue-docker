import os
from dataclasses import dataclass


@dataclass
class Settings:
    user: str
    password: str
    rabbitmq_address: str
    rabbitmq_logs_exchange: str



def _env():
    return Settings(
        user=os.environ["RABBITMQ_USER"],
        password=os.environ["RABBITMQ_PASSWORD"],
        rabbitmq_address=os.environ["RABBITMQ_ADDRESS"],
        rabbitmq_logs_exchange=os.environ["RABBITMQ_LOGS_EXCHANGE"],
    )

def _local():
    return None