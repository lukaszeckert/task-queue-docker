import os
import sched
import time
from http.client import HTTPException
from typing import Optional

import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi_utils.tasks import repeat_every

app = FastAPI()
s = sched.scheduler(time.time, time.sleep)

templates = Jinja2Templates(directory="src/server/fastapi/templates")


@app.get("/logs/")
def get_logs(request: Request, q: Optional[str] = None):
    res = os.listdir("logs/")
    if q:
        res = [_ for _ in res if q in res]
    return templates.TemplateResponse(
        "logs-list.html", {"request": request, "logs": res}
    )


@app.get("/logs/{item_id}")
def get_log(request: Request, item_id: str):
    if item_id not in os.listdir("logs"):
        raise HTTPException(status_code=404, detail=f"Item not found {item_id}")
    with open(os.path.join("logs", item_id)) as file:
        res = file.read()
    return templates.TemplateResponse("log.html", {"request": request, "log": res})


def print_event(sc):
    print("Hello")
    sc.enter(5, 1, print_event, (sc,))


@repeat_every(seconds=10)
@app.on_event("startup")
def start_scheduler():
    print("Hello")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
