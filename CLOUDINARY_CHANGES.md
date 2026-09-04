# Cloudinary integration — file-by-file changelist

Everything needed to move image + video storage onto Cloudinary. Files are listed
in dependency order; apply them top to bottom and run the migrations at the end.

**Behaviour summary**

- Images and videos upload to Cloudinary when credentials are present; otherwise
  they fall back to the local filesystem, so tests and fresh clones need no account.
- Cloudinary keeps images and videos under different *resource types* (an asset
  uploaded as an image cannot be served from the video endpoint), so there is one
  storage class per media kind.
- Storages are attached to model fields **as callables**, so migrations serialise
  them by reference and toggling `USE_CLOUDINARY` never generates a migration.
- New `FutsalMedia` gallery model + admin/public endpoints; user avatars reuse the
  same image storage and validators.

Files touched: 2 new modules, 2 new migrations, 1 new test file, and edits to
settings, validators, 2 models, serializers, views, both URL modules, requirements,
`.env.example` and the README.

---

## 1. `requirements.txt` — ADD

Append at the end:

```text
# Cloud media storage (images & videos)
cloudinary==1.46.2
django-cloudinary-storage==0.3.0
```

Then `pip install -r requirements.txt`. (`Pillow` is already required for `ImageField`.)

---

## 2. `.env.example` — ADD

Append at the end:

```env
# ---------------------------------------------------------------------------
# Cloudinary (images & videos)
# ---------------------------------------------------------------------------
# Grab these three from your Cloudinary dashboard. When all three are present
# uploads go to Cloudinary automatically; leave them blank to keep files on the
# local filesystem (MEDIA_ROOT) for local development and tests.
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

# Top-level folder every asset is nested under inside your Cloudinary account.
CLOUDINARY_FOLDER=futsal

# Force the storage backend on/off regardless of the credentials above.
# USE_CLOUDINARY=True

# Upload size limits, in megabytes.
MAX_IMAGE_UPLOAD_MB=5
MAX_VIDEO_UPLOAD_MB=100
```

Add the same three credentials to your real `.env` (and to your deploy target's
environment) when you want uploads to actually hit Cloudinary.

---

## 3. `config/settings/base.py` — EDIT (3 changes)

### 3a. Register the apps in `THIRD_PARTY_APPS`

```python
THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "drf_spectacular",
    "corsheaders",
    # Cloudinary must appear before staticfiles so its storage backends are
    # registered before Django resolves STORAGES.
    "cloudinary_storage",
    "cloudinary",
]
```

### 3b. Add the Cloudinary block right after `MEDIA_ROOT`

```python
# --- Cloudinary (images & videos) -----------------------------------------
# Cloudinary is used only when credentials are supplied, so local development
# and the test suite keep working against the filesystem with no extra setup.
CLOUDINARY_CLOUD_NAME = config("CLOUDINARY_CLOUD_NAME", default="")
CLOUDINARY_API_KEY = config("CLOUDINARY_API_KEY", default="")
CLOUDINARY_API_SECRET = config("CLOUDINARY_API_SECRET", default="")

USE_CLOUDINARY = config(
    "USE_CLOUDINARY",
    default=bool(CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET),
    cast=bool,
)

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": CLOUDINARY_CLOUD_NAME,
    "API_KEY": CLOUDINARY_API_KEY,
    "API_SECRET": CLOUDINARY_API_SECRET,
    "SECURE": True,
    # Keep every asset of this project under one Cloudinary folder.
    "PREFIX": config("CLOUDINARY_FOLDER", default="futsal"),
    # Fail loudly on upload errors instead of silently storing a broken URL.
    "MAGIC_FILE_PATH": "magic",
    "INVALID_VIDEO_ERROR_MESSAGE": "Please upload a valid video file.",
}

# Upload limits (enforced by the serializers in common.validators).
MAX_IMAGE_UPLOAD_MB = config("MAX_IMAGE_UPLOAD_MB", default=5, cast=int)
MAX_VIDEO_UPLOAD_MB = config("MAX_VIDEO_UPLOAD_MB", default=100, cast=int)

STORAGES = {
    "default": {
        "BACKEND": (
            "cloudinary_storage.storage.MediaCloudinaryStorage"
            if USE_CLOUDINARY
            else "django.core.files.storage.FileSystemStorage"
        )
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
    },
}
```

> `STORAGES` replaces the `DEFAULT_FILE_STORAGE` setting, which was removed in
> modern Django. If your project still runs Django < 4.2, use
> `DEFAULT_FILE_STORAGE = "..."` instead of the `STORAGES` dict.

### 3c. Add the Swagger tag (inside `SPECTACULAR_SETTINGS["TAGS"]`)

```python
{"name": "admin-media", "description": "Futsal image/video uploads (Cloudinary)"},
```

---

## 4. `common/storages.py` — NEW FILE

```python
"""Cloudinary storage backends.

Cloudinary serves three delivery types and they are NOT interchangeable — an
asset uploaded as ``image`` cannot be fetched from the ``video`` endpoint. These
thin subclasses make the intended resource type explicit at the field level:

    profile_image = models.ImageField(storage=image_storage, ...)
    highlight     = models.FileField(storage=video_storage, ...)
    invoice_pdf   = models.FileField(storage=raw_storage, ...)

When ``USE_CLOUDINARY`` is false every class falls back to Django's default
``FileSystemStorage``, so local development and the test suite never need
Cloudinary credentials or network access.
"""
from __future__ import annotations

from django.conf import settings
from django.core.files.storage import FileSystemStorage


def _cloudinary_enabled() -> bool:
    return bool(getattr(settings, "USE_CLOUDINARY", False))


from cloudinary_storage.storage import (  # noqa: E402  (needs configured settings)
    MediaCloudinaryStorage,
    RawMediaCloudinaryStorage,
    VideoMediaCloudinaryStorage,
)


class ImageStorage(MediaCloudinaryStorage):
    """Images (jpg, png, webp...). Cloudinary resource_type=image."""


class VideoStorage(VideoMediaCloudinaryStorage):
    """Videos (mp4, mov...). Cloudinary resource_type=video."""


class RawStorage(RawMediaCloudinaryStorage):
    """Any other file (pdf, csv...). Cloudinary resource_type=raw."""


def image_storage():
    """Callable storage for ImageField(storage=...).

    A callable is used rather than an instance so the choice is evaluated at
    runtime. Django also serialises the callable by reference in migrations,
    which means switching USE_CLOUDINARY never generates a new migration.
    """
    return ImageStorage() if _cloudinary_enabled() else FileSystemStorage()


def video_storage():
    return VideoStorage() if _cloudinary_enabled() else FileSystemStorage()


def raw_storage():
    return RawStorage() if _cloudinary_enabled() else FileSystemStorage()
```

---

## 5. `common/validators.py` — EDIT (append)

Append to the end of the file. It relies on the module's existing imports
(`from django.core.exceptions import ValidationError` and
`from django.utils.translation import gettext_lazy as _`) — add them if missing.

```python
IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
VIDEO_EXTENSIONS = {"mp4", "mov", "avi", "mkv", "webm"}


def _extension(name: str) -> str:
    return name.rsplit(".", 1)[-1].lower() if "." in (name or "") else ""


def _validate_upload(value, *, allowed: set[str], max_mb: int, label: str):
    """Shared size/extension check for uploaded media."""
    extension = _extension(getattr(value, "name", ""))
    if extension not in allowed:
        raise ValidationError(
            _("Unsupported %(label)s format '.%(ext)s'. Allowed: %(allowed)s.")
            % {"label": label, "ext": extension, "allowed": ", ".join(sorted(allowed))},
            code="invalid_extension",
        )
    size = getattr(value, "size", 0) or 0
    if size > max_mb * 1024 * 1024:
        raise ValidationError(
            _("%(label)s must be %(max)d MB or smaller.")
            % {"label": label.capitalize(), "max": max_mb},
            code="file_too_large",
        )
    return value


def validate_image_upload(value):
    """Validate an uploaded image against MAX_IMAGE_UPLOAD_MB."""
    from django.conf import settings

    return _validate_upload(
        value,
        allowed=IMAGE_EXTENSIONS,
        max_mb=getattr(settings, "MAX_IMAGE_UPLOAD_MB", 5),
        label="image",
    )


def validate_video_upload(value):
    """Validate an uploaded video against MAX_VIDEO_UPLOAD_MB."""
    from django.conf import settings

    return _validate_upload(
        value,
        allowed=VIDEO_EXTENSIONS,
        max_mb=getattr(settings, "MAX_VIDEO_UPLOAD_MB", 100),
        label="video",
    )
```

---

## 6. `accounts/models.py` — EDIT

Add the imports:

```python
from common.storages import image_storage
from common.validators import (
    validate_full_name, validate_image_upload, validate_phone_number,
)
```

Replace the `profile_image` field on `User` with:

```python
    profile_image = models.ImageField(
        upload_to="profiles/",
        storage=image_storage,
        validators=[validate_image_upload],
        blank=True,
        null=True,
    )
```

Note `storage=image_storage` — the function itself, **not** `image_storage()`.

---

## 7. `accounts/migrations/0002_alter_user_profile_image.py` — NEW

Generate it rather than copying, so it chains onto your latest migration:

```bash
python manage.py makemigrations accounts
```

It should contain a single `AlterField` on `profile_image` with
`storage=common.storages.image_storage` referenced by name.

---

## 8. `futsal/models.py` — EDIT (append model + imports)

Add the imports:

```python
from common.storages import image_storage, video_storage
from common.validators import validate_image_upload, validate_video_upload
```

Append the model:

```python
class FutsalMedia(BaseModel):
    """Gallery of images and videos for the futsal (served from Cloudinary).

    Image and video assets are stored under different Cloudinary resource types,
    so each media kind gets its own field with the matching storage backend.
    """

    class MediaType(models.TextChoices):
        IMAGE = "IMAGE", "Image"
        VIDEO = "VIDEO", "Video"

    futsal = models.ForeignKey(Futsal, on_delete=models.CASCADE, related_name="media")
    media_type = models.CharField(
        max_length=5, choices=MediaType.choices, default=MediaType.IMAGE, db_index=True
    )
    image = models.ImageField(
        upload_to="futsal/images/", storage=image_storage,
        validators=[validate_image_upload], blank=True, null=True,
    )
    video = models.FileField(
        upload_to="futsal/videos/", storage=video_storage,
        validators=[validate_video_upload], blank=True, null=True,
    )
    caption = models.CharField(max_length=255, blank=True, default="")
    is_cover = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    uploaded_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="uploaded_media",
    )

    class Meta:
        db_table = "futsal_media"
        ordering = ["sort_order", "-created_at"]
        constraints = [
            # Exactly one of image/video must be set, matching media_type.
            # Django stores an empty FileField as "" (not NULL), so both the
            # empty string and NULL count as "not provided".
            models.CheckConstraint(
                condition=(
                    models.Q(media_type="IMAGE")
                    & ~models.Q(image__in=["", None])
                    & models.Q(video__in=["", None])
                )
                | (
                    models.Q(media_type="VIDEO")
                    & ~models.Q(video__in=["", None])
                    & models.Q(image__in=["", None])
                ),
                name="media_matches_declared_type",
            ),
        ]
        indexes = [models.Index(fields=["futsal", "media_type"])]

    def __str__(self) -> str:
        return f"{self.media_type} for {self.futsal_id}"

    def save(self, *args, **kwargs):
        if self.futsal_id is None:
            self.futsal = Futsal.objects.get_solo()
        # Keep the unused column empty so the check constraint stays satisfied.
        if self.media_type == self.MediaType.IMAGE:
            self.video = ""
        else:
            self.image = ""
        super().save(*args, **kwargs)

    @property
    def file(self):
        """The populated asset, whichever kind it is."""
        return self.video if self.media_type == self.MediaType.VIDEO else self.image

    @property
    def url(self) -> str | None:
        asset = self.file
        return asset.url if asset else None
```

The check constraint compares against `["", None]` because Django writes an empty
`FileField` as `""`, not `NULL` — a plain `__isnull` check silently fails. `save()`
blanks the unused column so the constraint always holds.

`BaseModel` here is the project's abstract base (UUID pk + `created_at`/`updated_at`).

---

## 9. `futsal/migrations/0003_futsalmedia.py` — NEW

```bash
python manage.py makemigrations futsal
```

---

## 10. `futsal/serializers.py` — EDIT (add two serializers)

Add `FutsalMedia` to the models import, then add:

```python
class FutsalMediaSerializer(serializers.ModelSerializer):
    """Read representation: exposes the Cloudinary (or local) URL."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = FutsalMedia
        fields = ["id", "media_type", "url", "caption", "is_cover", "sort_order",
                  "created_at"]
        read_only_fields = fields

    def get_url(self, obj) -> str | None:
        return obj.url


class FutsalMediaUploadSerializer(serializers.ModelSerializer):
    """Upload an image or a video. Exactly one file field must be provided."""

    class Meta:
        model = FutsalMedia
        fields = ["id", "media_type", "image", "video", "caption", "is_cover",
                  "sort_order"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        media_type = attrs.get("media_type") or FutsalMedia.MediaType.IMAGE
        image = attrs.get("image")
        video = attrs.get("video")

        if image and video:
            raise serializers.ValidationError(
                {"video": ["Provide either an image or a video, not both."]}
            )
        if media_type == FutsalMedia.MediaType.IMAGE and not image:
            raise serializers.ValidationError(
                {"image": ["An image file is required when media_type is IMAGE."]}
            )
        if media_type == FutsalMedia.MediaType.VIDEO and not video:
            raise serializers.ValidationError(
                {"video": ["A video file is required when media_type is VIDEO."]}
            )
        attrs["media_type"] = media_type
        return attrs
```

---

## 11. `futsal/views.py` — EDIT (add two viewsets)

Add to the imports:

```python
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from futsal.models import Futsal, FutsalMedia
from futsal.serializers import FutsalMediaSerializer, FutsalMediaUploadSerializer
```

Append the viewsets:

```python
@extend_schema(tags=["admin-media"])
class AdminFutsalMediaViewSet(EnvelopeMixin, viewsets.ModelViewSet):
    """Upload and manage futsal images/videos stored on Cloudinary."""

    permission_classes = [IsAuthenticated, IsAdmin]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ["media_type", "is_cover"]
    ordering_fields = ["sort_order", "created_at"]
    ordering = ["sort_order", "-created_at"]

    def get_queryset(self):
        return FutsalMedia.objects.select_related("futsal")

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return FutsalMediaUploadSerializer
        return FutsalMediaSerializer

    @extend_schema(summary="Upload an image or video", responses={201: FutsalMediaSerializer})
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        media = serializer.save(
            futsal=Futsal.objects.get_solo(), uploaded_by=request.user
        )
        return success_response(
            data=FutsalMediaSerializer(media).data,
            message="Media uploaded successfully.",
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(summary="Update media metadata", responses={200: FutsalMediaSerializer})
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=kwargs.pop("partial", False))
        serializer.is_valid(raise_exception=True)
        media = serializer.save()
        return success_response(data=FutsalMediaSerializer(media).data,
                                message="Media updated successfully.")

    @extend_schema(
        summary="Delete media (also removes the asset from Cloudinary)",
        responses={200: OpenApiResponse(description="Media deleted successfully.")},
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        media_id = str(instance.id)
        asset = instance.file
        if asset:
            # Remove the remote asset first so Cloudinary does not accumulate orphans.
            asset.storage.delete(asset.name)
        instance.delete()
        return success_response(
            data={"id": media_id},
            message="Media deleted successfully.",
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["futsal"], summary="Public futsal gallery (images and videos)")
class PublicFutsalMediaViewSet(EnvelopeMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = FutsalMediaSerializer
    permission_classes = [AllowAny]
    filterset_fields = ["media_type", "is_cover"]
    ordering = ["sort_order", "-created_at"]

    def get_queryset(self):
        return FutsalMedia.objects.select_related("futsal")
```

`destroy()` deletes the remote Cloudinary asset **before** the database row, so a
deleted gallery item does not leave an orphaned file (and billable storage) behind.

---

## 12. `config/admin_urls.py` — EDIT

```python
from futsal.views import AdminFutsalMediaViewSet, AdminFutsalView, AdminSlotViewSet

# --- media (images & videos) -------------------------------------------------
media_router = DefaultRouter()
media_router.register("media", AdminFutsalMediaViewSet, basename="admin-media")
```

and inside `urlpatterns`, above the slot router:

```python
    path("", include(media_router.urls)),
```

---

## 13. `config/urls.py` — EDIT

```python
from futsal.views import FutsalDetailView, PublicFutsalMediaViewSet, PublicSlotViewSet

router.register("futsal-media", PublicFutsalMediaViewSet, basename="futsal-media")
```

---

## 14. `accounts/serializers.py` — EDIT

`UserSerializer` now returns a full URL for `profile_image` (the Cloudinary CDN URL
when enabled, an absolute local URL otherwise), and the profile update serializer
validates the upload.

Add to the imports:

```python
from common.validators import (
    validate_full_name, validate_image_upload, validate_phone_number,
)
```

Replace `UserSerializer` with:

```python
class UserSerializer(serializers.ModelSerializer):
    # Full URL (Cloudinary CDN when enabled, absolute local URL otherwise).
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "full_name", "email", "phone_number", "profile_image", "role",
                  "is_verified", "created_at"]
        read_only_fields = ["id", "role", "is_verified", "created_at"]

    def get_url(self, value) -> str | None:
        if not value:
            return None
        url = value.url
        request = self.context.get("request")
        if request is not None and url.startswith("/"):
            return request.build_absolute_uri(url)
        return url

    def get_profile_image(self, obj) -> str | None:
        return self.get_url(obj.profile_image)
```

Add this method to the profile-update serializer (`UserUpdateSerializer` /
`ProfileUpdateSerializer`):

```python
    def validate_profile_image(self, value):
        try:
            return validate_image_upload(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
```

---

## 15. `accounts/views.py` — EDIT

`UserSerializer` needs the request in its context to build absolute URLs. In the
profile view, pass it in both places:

```python
    def get(self, request):
        return success_response(
            data=UserSerializer(request.user, context={"request": request}).data,
            message="Profile retrieved successfully.")
```

```python
        user = serializer.save()
        return success_response(
            data=UserSerializer(user, context={"request": request}).data,
            message="Profile updated successfully.")
```

If the view does not already accept file uploads, add:

```python
    parser_classes = [MultiPartParser, FormParser, JSONParser]
```

---

## 16. `tests/test_media.py` — NEW FILE

20 tests covering storage selection, validation, permissions, the public gallery,
delete, and avatar upload. They run against the filesystem fallback, so no
Cloudinary credentials or network access are needed.

```python
"""Cloudinary-backed media uploads.

These tests run against the filesystem fallback (USE_CLOUDINARY=False in the
test settings) so no credentials or network access are needed. What they verify
is the wiring that is identical in both modes: storage selection, validation,
permissions and the API contract.
"""
from __future__ import annotations

import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from futsal.models import FutsalMedia

pytestmark = pytest.mark.django_db

ADMIN_MEDIA = "/api/v1/admin/media/"
PUBLIC_MEDIA = "/api/v1/futsal-media/"


def _png_bytes() -> bytes:
    """Smallest valid 1x1 PNG (Pillow validates ImageField content)."""
    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (1, 1), "green").save(buffer, format="PNG")
    return buffer.getvalue()


def image_file(name: str = "court.png") -> SimpleUploadedFile:
    return SimpleUploadedFile(name, _png_bytes(), content_type="image/png")


def video_file(name: str = "highlight.mp4") -> SimpleUploadedFile:
    return SimpleUploadedFile(name, b"\x00\x00\x00\x18ftypmp42fake", content_type="video/mp4")


# --------------------------------------------------------------- storage wiring
def test_storage_falls_back_to_filesystem_without_credentials(settings):
    from django.core.files.storage import FileSystemStorage

    from common.storages import image_storage, video_storage

    settings.USE_CLOUDINARY = False
    assert isinstance(image_storage(), FileSystemStorage)
    assert isinstance(video_storage(), FileSystemStorage)


def test_storage_switches_to_cloudinary_when_enabled(settings):
    from cloudinary_storage.storage import (
        MediaCloudinaryStorage, VideoMediaCloudinaryStorage,
    )

    from common.storages import image_storage, video_storage

    settings.USE_CLOUDINARY = True
    assert isinstance(image_storage(), MediaCloudinaryStorage)
    assert isinstance(video_storage(), VideoMediaCloudinaryStorage)


def test_image_and_video_use_different_cloudinary_resource_types(settings):
    """An image uploaded as a video resource type would 404 on delivery."""
    settings.USE_CLOUDINARY = True
    from common.storages import image_storage, video_storage

    assert image_storage().RESOURCE_TYPE == "image"
    assert video_storage().RESOURCE_TYPE == "video"


# --------------------------------------------------------------- uploads
def test_admin_can_upload_image(admin_client, futsal):
    response = admin_client.post(
        ADMIN_MEDIA, {"media_type": "IMAGE", "image": image_file(), "caption": "Main court"},
        format="multipart",
    )
    assert response.status_code == 201
    data = response.data["data"]
    assert data["media_type"] == "IMAGE"
    assert data["url"]
    assert FutsalMedia.objects.count() == 1


def test_admin_can_upload_video(admin_client, futsal):
    response = admin_client.post(
        ADMIN_MEDIA, {"media_type": "VIDEO", "video": video_file()}, format="multipart",
    )
    assert response.status_code == 201
    assert response.data["data"]["media_type"] == "VIDEO"


def test_upload_records_uploader_and_futsal(admin_client, futsal, admin_user):
    admin_client.post(ADMIN_MEDIA, {"media_type": "IMAGE", "image": image_file()},
                      format="multipart")
    media = FutsalMedia.objects.get()
    assert media.uploaded_by == admin_user
    assert media.futsal_id == futsal.id


# --------------------------------------------------------------- validation
def test_rejects_unsupported_image_extension(admin_client, futsal):
    bad = SimpleUploadedFile("script.svg", b"<svg/>", content_type="image/svg+xml")
    response = admin_client.post(ADMIN_MEDIA, {"media_type": "IMAGE", "image": bad},
                                 format="multipart")
    assert response.status_code == 400


def test_rejects_oversized_image(admin_client, futsal, settings):
    settings.MAX_IMAGE_UPLOAD_MB = 0  # nothing can be small enough
    response = admin_client.post(ADMIN_MEDIA, {"media_type": "IMAGE", "image": image_file()},
                                 format="multipart")
    assert response.status_code == 400
    assert "image" in response.data["errors"]


def test_image_declared_but_missing_is_rejected(admin_client, futsal):
    response = admin_client.post(ADMIN_MEDIA, {"media_type": "IMAGE"}, format="multipart")
    assert response.status_code == 400
    assert "image" in response.data["errors"]


def test_video_declared_but_missing_is_rejected(admin_client, futsal):
    response = admin_client.post(ADMIN_MEDIA, {"media_type": "VIDEO"}, format="multipart")
    assert response.status_code == 400
    assert "video" in response.data["errors"]


def test_cannot_upload_both_image_and_video(admin_client, futsal):
    response = admin_client.post(
        ADMIN_MEDIA,
        {"media_type": "IMAGE", "image": image_file(), "video": video_file()},
        format="multipart",
    )
    assert response.status_code == 400


# --------------------------------------------------------------- permissions
def test_normal_user_cannot_upload(user_client, futsal):
    response = user_client.post(ADMIN_MEDIA, {"media_type": "IMAGE", "image": image_file()},
                                format="multipart")
    assert response.status_code == 403


def test_unauthenticated_cannot_upload(api, futsal):
    response = api.post(ADMIN_MEDIA, {"media_type": "IMAGE", "image": image_file()},
                        format="multipart")
    assert response.status_code == 401


# --------------------------------------------------------------- public read
def test_public_gallery_is_readable(api, admin_client, futsal):
    admin_client.post(ADMIN_MEDIA, {"media_type": "IMAGE", "image": image_file()},
                      format="multipart")
    response = api.get(PUBLIC_MEDIA)
    assert response.status_code == 200
    assert response.data["data"]["count"] == 1
    assert response.data["data"]["results"][0]["url"]


def test_public_gallery_is_read_only(api, futsal):
    assert api.post(PUBLIC_MEDIA, {}, format="multipart").status_code in (401, 403, 405)


def test_gallery_filter_by_media_type(api, admin_client, futsal):
    admin_client.post(ADMIN_MEDIA, {"media_type": "IMAGE", "image": image_file()},
                      format="multipart")
    admin_client.post(ADMIN_MEDIA, {"media_type": "VIDEO", "video": video_file()},
                      format="multipart")
    assert api.get(f"{PUBLIC_MEDIA}?media_type=IMAGE").data["data"]["count"] == 1
    assert api.get(f"{PUBLIC_MEDIA}?media_type=VIDEO").data["data"]["count"] == 1


# --------------------------------------------------------------- delete
def test_delete_removes_record_and_returns_envelope(admin_client, futsal):
    admin_client.post(ADMIN_MEDIA, {"media_type": "IMAGE", "image": image_file()},
                      format="multipart")
    media = FutsalMedia.objects.get()
    response = admin_client.delete(f"{ADMIN_MEDIA}{media.id}/")
    assert response.status_code == 200
    assert response.data["message"] == "Media deleted successfully."
    assert FutsalMedia.objects.count() == 0


# --------------------------------------------------------------- profile image
def test_user_can_upload_profile_image(user_client, user):
    response = user_client.patch("/api/v1/users/me/", {"profile_image": image_file()},
                                 format="multipart")
    assert response.status_code == 200
    assert response.data["data"]["profile_image"]
    user.refresh_from_db()
    assert user.profile_image


def test_profile_image_rejects_bad_extension(user_client):
    bad = SimpleUploadedFile("notes.txt", b"hello", content_type="text/plain")
    response = user_client.patch("/api/v1/users/me/", {"profile_image": bad},
                                 format="multipart")
    assert response.status_code == 400


def test_profile_image_url_is_absolute(user_client):
    user_client.patch("/api/v1/users/me/", {"profile_image": image_file()},
                      format="multipart")
    url = user_client.get("/api/v1/users/me/").data["data"]["profile_image"]
    assert url.startswith("http")
```

---

## 17. `config/settings/test.py` — EDIT (important)

Once real credentials exist in `.env`, the test suite would otherwise upload to
your **live Cloudinary account** on every run. Pin it off explicitly:

```python
# Never touch a real Cloudinary account from the test suite, even when the
# developer's .env has live credentials. Uploads go to a temp filesystem dir.
USE_CLOUDINARY = False
MEDIA_ROOT = BASE_DIR / "test_media"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
```

---

## 18. `common/exception_handlers.py` — EDIT

When Cloudinary refuses an asset (corrupt file, unsupported codec, plan limit)
the SDK raises `cloudinary.exceptions.BadRequest`. DRF does not recognise it, so
it fell through to a **500 with an empty `errors` object**. It is the client's
input, so it should be a 400.

Add this helper above `custom_exception_handler`:

```python
def _is_upload_rejection(exc) -> bool:
    """True for a 4xx-style rejection raised by the Cloudinary SDK.

    Imported lazily and matched by class name so the project still runs when
    cloudinary is not installed (e.g. a slimmed-down test image).
    """
    try:
        from cloudinary.exceptions import BadRequest, Error, NotAllowed
    except ImportError:  # pragma: no cover - cloudinary always installed here
        return False
    if isinstance(exc, (BadRequest, NotAllowed)):
        return True
    # Some SDK paths raise the generic Error for validation problems.
    return isinstance(exc, Error) and "unsupported" in str(exc).lower()
```

and this branch at the top of `custom_exception_handler`, **before**
`response = drf_exception_handler(exc, context)`:

```python
    if _is_upload_rejection(exc):
        # Cloudinary refused the asset (bad/corrupt file, unsupported codec,
        # account limit). That is the client's input, not a server fault.
        logger.warning("Media upload rejected by storage backend: %s", exc)
        return Response(
            {
                "success": False,
                "message": "Validation failed.",
                "errors": {"file": [str(exc) or "The uploaded file was rejected."]},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
```

Result:

```json
{"success": false, "message": "Validation failed.",
 "errors": {"file": ["Unsupported video format or file"]}}
```

---

## 19. `README.md` — EDIT

A new **Media storage (Cloudinary)** section was added before *6. API documentation*
covering the env vars, the auto-detect switch, resource types, the size/extension
limits table, the endpoint table and a `curl` upload example.

---

## Apply & verify

```bash
pip install -r requirements.txt
python manage.py makemigrations          # -> accounts 0002, futsal 0003
python manage.py migrate
pytest                                   # 217 passed
python manage.py spectacular --file schema.yaml   # 0 errors, 0 warnings
```

Smoke test:

```bash
curl -X POST http://localhost:8000/api/v1/admin/media/ \
  -H "Authorization: Bearer $ACCESS" \
  -F media_type=IMAGE -F image=@court.png -F "caption=Main court"

curl http://localhost:8000/api/v1/futsal-media/
```

## New endpoints

| Method | Path | Auth |
| --- | --- | --- |
| `GET` | `/api/v1/futsal-media/` | public (`?media_type=IMAGE\|VIDEO`, `?is_cover=true`) |
| `GET` | `/api/v1/futsal-media/{id}/` | public |
| `GET` `POST` | `/api/v1/admin/media/` | admin |
| `GET` `PATCH` `DELETE` | `/api/v1/admin/media/{id}/` | admin |
| `PATCH` | `/api/v1/users/me/` | authenticated — `profile_image` upload |

## New environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `CLOUDINARY_CLOUD_NAME` | `""` | Cloudinary account |
| `CLOUDINARY_API_KEY` | `""` | Cloudinary account |
| `CLOUDINARY_API_SECRET` | `""` | Cloudinary account |
| `CLOUDINARY_FOLDER` | `futsal` | Folder prefix for all assets |
| `USE_CLOUDINARY` | auto (true when all 3 creds set) | Force storage backend on/off |
| `MAX_IMAGE_UPLOAD_MB` | `5` | Image size cap |
| `MAX_VIDEO_UPLOAD_MB` | `100` | Video size cap |
