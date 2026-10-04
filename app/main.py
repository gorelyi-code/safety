"""HTTP API of the service."""

import asyncio
import contextlib
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response

from app import __version__
from app.config import settings
from app.processing import process_image
from app.storage import Storage
from app.validation import UploadError, detect_format, read_limited

storage = Storage(settings.storage_dir, settings.retention_seconds)


async def _cleanup_loop() -> None:
    while True:
        storage.cleanup_expired()
        await asyncio.sleep(settings.cleanup_interval_seconds)


@asynccontextmanager
async def lifespan(_: FastAPI):
    task = asyncio.create_task(_cleanup_loop())
    yield
    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await task


app = FastAPI(title="ImgDrop", version=__version__, lifespan=lifespan)


@app.exception_handler(UploadError)
async def upload_error_handler(_: Request, exc: UploadError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": __version__}


@app.post("/files", status_code=201)
async def upload_file(file: UploadFile = File(...)) -> dict:
    data = await read_limited(file, settings.max_upload_bytes)
    image_format = detect_format(data)
    result = process_image(data, image_format, settings.max_pixels, settings.thumbnail_size)
    meta = {
        **result.metadata,
        "size_bytes": len(data),
        "original_filename": file.filename,
        "declared_content_type": file.content_type,
    }
    return storage.save(data, result.thumbnail_png, meta)


@app.get("/files/{file_id}")
def get_file_meta(file_id: str) -> dict:
    meta = storage.get_meta(file_id)
    if meta is None:
        raise HTTPException(status_code=404, detail="File not found")
    return meta


@app.get("/files/{file_id}/thumbnail")
def get_thumbnail(file_id: str) -> FileResponse:
    path = storage.thumbnail_path(file_id)
    if path is None:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type="image/png")


@app.delete("/files/{file_id}", status_code=204)
def delete_file(file_id: str) -> Response:
    if not storage.delete(file_id):
        raise HTTPException(status_code=404, detail="File not found")
    return Response(status_code=204)
