from fastapi import FastAPI

from supermoon_client.routers.api import router as api

app = FastAPI()

app.include_router(api)
