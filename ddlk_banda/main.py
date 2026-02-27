from fastapi import FastAPI

from ddlk_banda.api.topics import router as topics_router

app = FastAPI(title="ddlk-banda")
app.include_router(topics_router)
