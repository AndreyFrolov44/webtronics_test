from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import init_db
from db.base import database
from routers import router

app = FastAPI()
app.include_router(router)


origins = ['http://localhost']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
def root():
    return {"message": "hello"}


@app.on_event("startup")
async def startup():
    init_db()
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()