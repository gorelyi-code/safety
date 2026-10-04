"""Generate a small set of safe local sample files in ./samples for manual runs."""

import io
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "samples"


def png_bytes(size=(640, 480), color=(30, 120, 200)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, format="PNG")
    return buffer.getvalue()


def jpeg_bytes(size=(800, 600), color=(200, 80, 40)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, format="JPEG")
    return buffer.getvalue()


def main() -> None:
    OUT.mkdir(exist_ok=True)
    png = png_bytes()
    samples = {
        "valid.png": png,
        "valid.jpg": jpeg_bytes(),
        "truncated.png": png[: len(png) // 2],
        "fake.png": b"this is plain text, not an image\n",
        "empty.png": b"",
        "too_large.bin": b"\x89PNG\r\n\x1a\n" + b"\0" * (6 * 1024 * 1024),
    }
    for name, data in samples.items():
        (OUT / name).write_bytes(data)
        print(f"{OUT / name} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
