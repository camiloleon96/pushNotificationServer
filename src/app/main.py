from fastapi import FastAPI
from fastapi.responses import JSONResponse
from database import Base
from database import engine
from routers import user, subscription

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}


app.include_router(user.router, prefix="/api")
app.include_router(subscription.router, prefix="/api")
