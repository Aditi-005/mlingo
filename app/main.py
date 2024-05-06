from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.database import engine
from app.v1.application import api_interceptor
from app.v1.domain import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

app.include_router(api_interceptor.router)
