from fastapi import FastAPI

from ddlk_banda.api.topics import router as topics_router
from ddlk_banda.config import settings
from ddlk_banda.db.models import Base
from ddlk_banda.db.session import engine

app = FastAPI(title=settings.app_name)
app.include_router(topics_router)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}
