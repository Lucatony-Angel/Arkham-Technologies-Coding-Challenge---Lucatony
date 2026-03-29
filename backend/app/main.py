from fastapi import FastAPI
from backend.app.api.routes import router

app = FastAPI(title="Nuclear Outages API")

app.include_router(router)