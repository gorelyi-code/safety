"""Checks applied to an upload before it is stored or decoded."""

from fastapi import UploadFile

CHUNK_SIZE = 64 * 1024

# The file type is decided by the leading bytes only. The client-supplied
# filename and Content-Type are kept as metadata and never trusted.
SIGNATURES = {
    b"\x89PNG\r\n\x1a\n": "PNG",
    b"\xff\xd8\xff": "JPEG",
}


class UploadError(Exception):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


async def read_limited(upload: UploadFile, max_bytes: int) -> bytes:
    """Read the upload in chunks and stop as soon as it exceeds max_bytes."""
    chunks = []
    total = 0
    while chunk := await upload.read(CHUNK_SIZE):
        total += len(chunk)
        if total > max_bytes:
            raise UploadError(413, f"File is larger than {max_bytes} bytes")
        chunks.append(chunk)
    if total == 0:
        raise UploadError(400, "File is empty")
    return b"".join(chunks)


def detect_format(data: bytes) -> str:
    for signature, name in SIGNATURES.items():
        if data.startswith(signature):
            return name
    raise UploadError(415, "Only PNG and JPEG images are supported")
