from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(title="ARE Spectacle v2")
app.include_router(router)
