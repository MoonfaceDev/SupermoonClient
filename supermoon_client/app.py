from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from supermoon_client.routers.api import router as api

app = FastAPI()

app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
