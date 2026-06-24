from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Sentinel",
    description="Infrastructure security monitoring with real-time packet analysis, service health checks, and intelligent alerting.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "sentinel",
        "version": "0.1.0",
        "env": settings.app_env,
    }