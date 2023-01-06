from celery import Celery

from src.common.rabbitmq_logger import RabbitMQLogger
from src.common.settings import _env
# from src.common.rabbitmq_logger import RabbitMQLogger
from src.common.tasks import Add

settings = _env()

print(settings)

rabbit_logger = RabbitMQLogger(user=settings.user, password=settings.password, exchange=settings.rabbitmq_logs_exchange, rabbitmq_address=settings.rabbitmq_address)

app = Celery(
    "task-queue",
    backend=f"rpc://",
    broker=f"pyamqp://{settings.user}:{settings.password}@{settings.rabbitmq_address}/",
)
app.conf.update(
    CELERYD_PREFETCH_MULTIPLIER=1,
    CELERY_IGNORE_RESULT=False,
)

app.register_task(Add(rabbit_logger))

if __name__ == "__main__":
    app.start()
