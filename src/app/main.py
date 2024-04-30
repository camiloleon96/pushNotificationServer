from fastapi import FastAPI
from fastapi.responses import JSONResponse
from database import Base
from database import engine
from routers import user, subscription
from worker_task_definition import create_task

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}


@app.post("/ex1")
def run_task():
    task = create_task.delay('user1234')
    return JSONResponse({"Result": task.get()})


app.include_router(user.router)
app.include_router(subscription.router)
