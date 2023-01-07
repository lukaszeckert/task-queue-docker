import sched
import time
from threading import Thread

import uvicorn
from fastapi import FastAPI

app = FastAPI()
s = sched.scheduler(time.time, time.sleep)


def print_event(sc):
    print("Hello")
    sc.enter(5, 1, print_event, (sc,))


def start_scheduler():
    s.enter(5, 1, print_event, (s,))
    s.run()


@app.on_event("startup")
async def startup_event():
    thread = Thread(target=start_scheduler)
    thread.start()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
