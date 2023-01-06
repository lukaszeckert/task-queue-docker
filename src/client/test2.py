import itertools
import time


from src.common.rabbitmq_logger import RabbitMQLogger
from src.common.settings import get_settings

settings = get_settings("environment")

rabbit_logger = RabbitMQLogger(
    user=settings.user,
    password=settings.password,
    exchange=settings.rabbitmq_logs_exchange,
    rabbitmq_address=settings.rabbitmq_address,
)
rabbit_logger.bind("*")


def read_until_none():
    while True:
        key, msg = rabbit_logger.read_one()
        if key is not None:
            yield key, msg
        else:
            break


while True:
    massages = list(read_until_none())
    groups = itertools.groupby(massages, key=lambda x: x[0])
    for g, values in groups:
        with open(f"logs/{g}.log", mode="a+") as file:
            extracted_values = [_[1] for _ in values]
            file.writelines(extracted_values)
    time.sleep(1)
