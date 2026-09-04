"""Coverage for Cloudinary-wired gallery and profile media APIs.

The test settings keep USE_CLOUDINARY disabled, exercising the local fallback
without network access.
"""
from __future__ import annotations

import io

import pytest
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from futsal.models import FutsalMedia


pytestmark = pytest.mark.django_db
ADMIN_MEDIA = "/api/v1/admin/media/"
PUBLIC_MEDIA = "/api/v1/futsal-media/"


def image_file(name="court.png"):
    data = io.BytesIO()
    Image.new("RGB", (1, 1), "green").save(data, format="PNG")
    return SimpleUploadedFile(name, data.getvalue(), content_type="image/png")


def video_file(name="highlight.mp4"):
    return SimpleUploadedFile(name, b"\x00\x00\x00\x18ftypmp42fake", content_type="video/mp4")


def test_storage_falls_back_to_filesystem(settings):
    from common.storages import image_storage, video_storage

    settings.USE_CLOUDINARY = False
    assert isinstance(image_storage(), FileSystemStorage)
    assert isinstance(video_storage(), FileSystemStorage)


def test_admin_can_upload_and_public_can_read_image(admin_client, futsal):
    response = admin_client.post(
        ADMIN_MEDIA, {"media_type": "IMAGE", "image": image_file(), "caption": "Main court"},
        format="multipart",
    )
    assert response.status_code == 201
    assert response.data["data"]["url"]
    assert FutsalMedia.objects.count() == 1
    assert admin_client.get(PUBLIC_MEDIA).data["data"]["count"] == 1


def test_admin_can_upload_video(admin_client, futsal):
    response = admin_client.post(
        ADMIN_MEDIA, {"media_type": "VIDEO", "video": video_file()}, format="multipart"
    )
    assert response.status_code == 201
    assert response.data["data"]["media_type"] == "VIDEO"


def test_invalid_media_upload_is_rejected(admin_client, futsal):
    bad = SimpleUploadedFile("court.svg", b"<svg/>", content_type="image/svg+xml")
    response = admin_client.post(ADMIN_MEDIA, {"media_type": "IMAGE", "image": bad}, format="multipart")
    assert response.status_code == 400


def test_normal_user_cannot_upload_media(user_client, futsal):
    response = user_client.post(ADMIN_MEDIA, {"media_type": "IMAGE", "image": image_file()}, format="multipart")
    assert response.status_code == 403


def test_media_metadata_can_be_updated_and_deleted(admin_client, futsal):
    admin_client.post(ADMIN_MEDIA, {"media_type": "IMAGE", "image": image_file()}, format="multipart")
    media = FutsalMedia.objects.get()
    response = admin_client.patch(f"{ADMIN_MEDIA}{media.id}/", {"caption": "New caption"}, format="json")
    assert response.status_code == 200
    assert response.data["data"]["caption"] == "New caption"
    assert admin_client.delete(f"{ADMIN_MEDIA}{media.id}/").status_code == 200
    assert not FutsalMedia.objects.exists()


def test_user_can_upload_profile_image(user_client, user):
    response = user_client.patch("/api/v1/users/me/", {"profile_image": image_file()}, format="multipart")
    assert response.status_code == 200
    assert response.data["data"]["profile_image"].startswith("http")
