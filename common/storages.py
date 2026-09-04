"""Cloudinary storage helpers with a local filesystem fallback."""
from __future__ import annotations

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from cloudinary_storage.storage import (
    MediaCloudinaryStorage,
    RawMediaCloudinaryStorage,
    VideoMediaCloudinaryStorage,
)


def _cloudinary_enabled() -> bool:
    return bool(getattr(settings, "USE_CLOUDINARY", False))


class ImageStorage(MediaCloudinaryStorage):
    """Cloudinary image resource storage."""


class VideoStorage(VideoMediaCloudinaryStorage):
    """Cloudinary video resource storage."""


class RawStorage(RawMediaCloudinaryStorage):
    """Cloudinary raw resource storage."""


def image_storage():
    return ImageStorage() if _cloudinary_enabled() else FileSystemStorage()


def video_storage():
    return VideoStorage() if _cloudinary_enabled() else FileSystemStorage()


def raw_storage():
    return RawStorage() if _cloudinary_enabled() else FileSystemStorage()
