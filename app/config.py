"""Service limits. Every value can be overridden with an environment variable."""

import os
from dataclasses import dataclass
from pathlib import Path


def _int_env(name: str, default: int) -> int:
    value = os.environ.get(name)
    return int(value) if value else default


@dataclass(frozen=True)
class Settings:
    storage_dir: Path
    max_upload_bytes: int
    max_pixels: int
    thumbnail_size: int
    retention_seconds: int
    cleanup_interval_seconds: int


def load_settings() -> Settings:
    return Settings(
        storage_dir=Path(os.environ.get("STORAGE_DIR", "./data")).resolve(),
        max_upload_bytes=_int_env("MAX_UPLOAD_BYTES", 5 * 1024 * 1024),
        max_pixels=_int_env("MAX_PIXELS", 25_000_000),
        thumbnail_size=_int_env("THUMBNAIL_SIZE", 256),
        retention_seconds=_int_env("RETENTION_SECONDS", 3600),
        cleanup_interval_seconds=_int_env("CLEANUP_INTERVAL_SECONDS", 60),
    )


settings = load_settings()
