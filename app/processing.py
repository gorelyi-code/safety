"""Image decoding, metadata extraction and thumbnail creation (Pillow)."""

import io
import warnings
from dataclasses import dataclass

from PIL import Image, ImageOps, UnidentifiedImageError

from app.validation import UploadError


@dataclass
class ProcessingResult:
    metadata: dict
    thumbnail_png: bytes


def process_image(data: bytes, expected_format: str, max_pixels: int, thumbnail_size: int) -> ProcessingResult:
    # Pillow only warns between max_pixels and 2 * max_pixels; turn the warning
    # into an error so the limit is a hard one.
    Image.MAX_IMAGE_PIXELS = max_pixels
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)

            with Image.open(io.BytesIO(data)) as probe:
                probe.verify()

            # verify() leaves the image unusable, so open it again to decode.
            with Image.open(io.BytesIO(data)) as image:
                if image.format != expected_format:
                    raise UploadError(415, "File content does not match its signature")
                metadata = {
                    "format": image.format,
                    "width": image.width,
                    "height": image.height,
                    "mode": image.mode,
                }
                thumbnail = ImageOps.exif_transpose(image)
                thumbnail.thumbnail((thumbnail_size, thumbnail_size))
                if thumbnail.mode not in ("RGB", "RGBA", "L", "LA"):
                    thumbnail = thumbnail.convert("RGBA")
                buffer = io.BytesIO()
                thumbnail.save(buffer, format="PNG")
    except (Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise UploadError(413, f"Image has more than {max_pixels} pixels")
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError):
        raise UploadError(422, "Image is corrupted or cannot be decoded")

    return ProcessingResult(metadata=metadata, thumbnail_png=buffer.getvalue())
