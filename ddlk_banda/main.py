from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from ddlk_banda.api.demo import router as demo_router
from ddlk_banda.api.topics import router as topics_router
from ddlk_banda.config import settings
from ddlk_banda.db.models import Base
from ddlk_banda.db.session import engine

app = FastAPI(title=settings.app_name)
app.include_router(topics_router)
app.include_router(demo_router)
app.mount("/web", StaticFiles(directory="web"), name="web")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}


@app.get("/")
def root() -> FileResponse:
    return FileResponse("web/index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("ddlk_banda.main:app", host="127.0.0.1", port=8000, reload=False)
