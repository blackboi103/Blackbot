from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = PROJECT_ROOT / "static"


app = FastAPI(title="OpenClaw WebUI")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
async def serve_frontend() -> FileResponse:
  return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health_check() -> dict[str, str]:
  return {"status": "ok"}