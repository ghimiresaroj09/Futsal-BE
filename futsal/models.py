"""Futsal venue and date-wise slot models."""
from __future__ import annotations

import datetime as dt

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from common.enums import FutsalStatus, SlotStatus
from common.models import BaseModel
from common.storages import image_storage, video_storage
from common.utils import combine_local, local_now
from common.validators import validate_image_upload, validate_video_upload


class FutsalManager(models.Manager):
    """Manager for the single futsal venue configured in this system."""

    def get_solo(self) -> "Futsal":
        """Return the one and only futsal, creating a default if none exists."""
        futsal = self.first()
        if futsal is None:
            futsal = self.create(
                name="Futsal",
                location="",
                price_per_slot=0,
                slot_duration=60,
                opening_time=dt.time(6, 0),
                closing_time=dt.time(22, 0),
            )
        return futsal


class Futsal(BaseModel):
    """Singleton venue configuration.

    This system manages exactly ONE futsal. The model is kept as a table (rather
    than settings) so pricing and opening hours stay editable at runtime, but a
    second row can never be created.
    """

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, default="")
    location = models.CharField(max_length=150)
    address = models.CharField(max_length=255, blank=True, default="")
    phone = models.CharField(max_length=20, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    price_per_slot = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    slot_duration = models.PositiveIntegerField(default=60, help_text="Minutes")
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    status = models.CharField(
        max_length=10, choices=FutsalStatus.choices, default=FutsalStatus.ACTIVE, db_index=True
    )

    objects = FutsalManager()

    class Meta:
        db_table = "futsal_futsal"
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price_per_slot__gte=0), name="futsal_price_non_negative"
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if self._state.adding and Futsal.objects.exists():
            raise ValidationError(
                "Only one futsal can exist in this system. Update the existing one instead."
            )
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.opening_time and self.closing_time and self.opening_time >= self.closing_time:
            raise ValidationError({"closing_time": "Closing time must be after opening time."})


class SlotQuerySet(models.QuerySet):
    def available(self):
        return self.filter(status=SlotStatus.AVAILABLE)

    def for_date(self, date):
        return self.filter(date=date)

    def upcoming(self):
        return self.filter(date__gte=local_now().date())


class Slot(BaseModel):
    """A one-hour, whole-hour bookable slot on a given date (e.g. 07:00 - 08:00)."""

    futsal = models.ForeignKey(Futsal, on_delete=models.CASCADE, related_name="slots")
    date = models.DateField(db_index=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                help_text="Overrides futsal price when set.")
    status = models.CharField(
        max_length=10, choices=SlotStatus.choices, default=SlotStatus.AVAILABLE, db_index=True
    )

    objects = SlotQuerySet.as_manager()

    class Meta:
        db_table = "futsal_slot"
        ordering = ["date", "start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["futsal", "date", "start_time"], name="uniq_slot_per_futsal_datetime"
            ),
            models.CheckConstraint(
                condition=models.Q(start_time__lt=models.F("end_time")),
                name="slot_start_before_end",
            ),
        ]
        indexes = [
            models.Index(fields=["date", "status"]),
            models.Index(fields=["futsal", "date", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.date} {self.start_time:%H:%M}-{self.end_time:%H:%M}"

    def save(self, *args, **kwargs):
        if self.futsal_id is None:
            self.futsal = Futsal.objects.get_solo()
        super().save(*args, **kwargs)

    @property
    def effective_price(self):
        return self.price if self.price is not None else self.futsal.price_per_slot

    @property
    def start_datetime(self):
        return combine_local(self.date, self.start_time)

    @property
    def end_datetime(self):
        return combine_local(self.date, self.end_time)

    @property
    def is_past(self) -> bool:
        return self.start_datetime <= local_now()


class ClosureQuerySet(models.QuerySet):
    def covering(self, date: dt.date):
        return self.filter(date=date)


class FutsalClosure(BaseModel):
    """A whole day on which the futsal is closed (holiday, maintenance, private hire).

    Persisting closures — rather than only flipping slot statuses — means the
    reason is auditable and slot generation will not silently repopulate the day.
    """

    futsal = models.ForeignKey(Futsal, on_delete=models.CASCADE, related_name="closures")
    date = models.DateField(db_index=True)
    reason = models.CharField(max_length=255, blank=True, default="")
    created_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="futsal_closures",
    )

    objects = ClosureQuerySet.as_manager()

    class Meta:
        db_table = "futsal_closure"
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(fields=["futsal", "date"], name="uniq_closure_per_date"),
        ]

    def __str__(self) -> str:
        return f"Closed {self.date}"

    def save(self, *args, **kwargs):
        if self.futsal_id is None:
            self.futsal = Futsal.objects.get_solo()
        super().save(*args, **kwargs)


class FutsalMedia(BaseModel):
    """Image and video gallery for the single futsal venue."""

    class MediaType(models.TextChoices):
        IMAGE = "IMAGE", "Image"
        VIDEO = "VIDEO", "Video"

    futsal = models.ForeignKey(Futsal, on_delete=models.CASCADE, related_name="media")
    media_type = models.CharField(max_length=5, choices=MediaType.choices,
                                  default=MediaType.IMAGE, db_index=True)
    image = models.ImageField(upload_to="futsal/images/", storage=image_storage,
                              validators=[validate_image_upload], blank=True, null=True)
    video = models.FileField(upload_to="futsal/videos/", storage=video_storage,
                             validators=[validate_video_upload], blank=True, null=True)
    caption = models.CharField(max_length=255, blank=True, default="")
    is_cover = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    uploaded_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name="uploaded_media")

    class Meta:
        db_table = "futsal_media"
        ordering = ["sort_order", "-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(media_type="IMAGE") & ~models.Q(image__in=["", None])
                    & models.Q(video__in=["", None])
                ) | (
                    models.Q(media_type="VIDEO") & ~models.Q(video__in=["", None])
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
        if self.media_type == self.MediaType.IMAGE:
            self.video = ""
        else:
            self.image = ""
        super().save(*args, **kwargs)

    @property
    def file(self):
        return self.video if self.media_type == self.MediaType.VIDEO else self.image

    @property
    def url(self) -> str | None:
        return self.file.url if self.file else None
