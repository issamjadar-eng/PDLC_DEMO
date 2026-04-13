from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from console.auth import preflight
from console.chat.router import router as chat_router
from console.documents.router import router as documents_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    preflight()
    yield


app = FastAPI(title="PDLC Project Console", lifespan=lifespan)
app.include_router(chat_router)
app.include_router(documents_router)

_static_dir = Path(__file__).parent / "web" / "static"
app.mount("/static", StaticFiles(directory=_static_dir), name="static")
