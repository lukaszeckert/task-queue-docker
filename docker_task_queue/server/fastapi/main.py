import itertools
import os
import sched
import time
from http.client import HTTPException
from typing import List, Optional, Tuple

import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi_utils.tasks import repeat_every
from docker_task_queue.common.rabbitmq_logger import RabbitMQLogger
from docker_task_queue.common.settings import get_settings

rabbit_logger: RabbitMQLogger
queue_name = os.environ.get("QUEUE_NAME", "all_logs")
logs_dir = os.environ.get("LOG_DIR", "logs")

app = FastAPI()
s = sched.scheduler(time.time, time.sleep)

templates = Jinja2Templates(directory="docker_task_queue/server/fastapi/templates")


@app.get("/logs/")
def get_logs(request: Request, q: Optional[str] = None):
    res = os.listdir("logs/")
    if q:
        res = [_ for _ in res if q in res]
    return templates.TemplateResponse(
        "logs-list.html", {"request": request, "logs": res}
    )


def is_safe_path(basedir, path, follow_symlinks=True):
    # resolves symbolic links
    if follow_symlinks:
        matchpath = os.path.realpath(path)
    else:
        matchpath = os.path.abspath(path)
    return basedir == os.path.commonpath((basedir, matchpath))


@app.get("/logs/{item_id}")
def get_log(request: Request, item_id: str):
    if item_id not in os.listdir(logs_dir) or not is_safe_path(logs_dir, item_id):
        raise HTTPException(status_code=404, detail=f"Item not found {item_id}")  # type: ignore
    with open(os.path.join("logs", item_id)) as file:
        res = file.read()
    return templates.TemplateResponse("log.html", {"request": request, "log": res})


def read_until_none(max_messages: int = 1000) -> List[Tuple[str, str]]:
    res: List[Tuple[str, str]] = []

    for _ in range(max_messages):
        key, message_count, msg = rabbit_logger.read_one()
        if key is not None:
            res.append((key, msg))
        else:
            break
    return res


@app.on_event("startup")
def setup_rabbitmq_loger():
    global rabbit_logger
    settings = get_settings("environment")

    rabbit_logger = RabbitMQLogger(
        user=settings.user,
        password=settings.password,
        exchange=settings.rabbitmq_logs_exchange,
        rabbitmq_address=settings.rabbitmq_address,
    )
    rabbit_logger.bind("*", queue_name, False)


@repeat_every(seconds=10)
@app.on_event("startup")
def start_scheduler():
    massages = read_until_none()
    groups = itertools.groupby(massages, key=lambda x: x[0])
    for g, values in groups:
        with open(f"logs/{g}.log", mode="a+") as file:
            extracted_values = [_[1] for _ in values]
            file.writelines(extracted_values)
            file.flush()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


while True:
    time.sleep(1)
