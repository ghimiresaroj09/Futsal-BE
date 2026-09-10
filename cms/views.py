"""CMS API views for serving homepage content."""
from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny

from cms.selectors import (
    get_about_page_data,
    get_bookings_page_data,
    get_contact_page_data,
    get_gallery_page_data,
    get_homepage_data,
)
from cms.serializers import (
    AboutPageSerializer,
    BookingsPageSerializer,
    ContactPageSerializer,
    GalleryPageSerializer,
    HomepageSerializer,
)
from cms.services import (
    update_about_page_content,
    update_bookings_page_content,
    update_contact_page_content,
    update_gallery_page_content,
    update_homepage_content,
)
from common.permissions import IsAdmin
from common.responses import success_response


@extend_schema(
    tags=["cms"],
    summary="Get homepage content",
    description=(
        "Returns all homepage sections in render order: "
        "Hero → Stats → Arena → Features → How it works → Gallery preview → "
        "Testimonials → CTA banner. "
        "\n\n"
        "The live status chip (open/closed + next free slot) is NOT part of this response. "
        "The frontend computes it from `/api/v1/futsal/` hours and "
        "`/api/v1/slots/date-wise/` for today."
    ),
    responses={200: HomepageSerializer},
)
class HomepageView(GenericAPIView):
    """
    Public API for homepage content.
    
    GET: Returns structured content for all homepage sections (public, cached)
    PATCH: Updates homepage content (admin-only)
    """
    
    serializer_class = HomepageSerializer
    
    def get_permissions(self):
        """Public for GET, admin-only for PATCH."""
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdmin()]
    
    def get(self, request):
        """Retrieve complete homepage content."""
        data = get_homepage_data()
        serializer = self.get_serializer(data)
        return success_response(
            data=serializer.data,
            message="Homepage content retrieved successfully."
        )
    
    @extend_schema(
        summary="Update homepage content",
        description="Updates homepage content. Only modified fields need to be provided.",
        request=HomepageSerializer,
        responses={200: HomepageSerializer},
    )
    def patch(self, request):
        """Update homepage content (admin-only)."""
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        updated_data = update_homepage_content(serializer.validated_data)
        response_serializer = self.get_serializer(updated_data)
        
        return success_response(
            data=response_serializer.data,
            message="Homepage content updated successfully.",
            status=status.HTTP_200_OK
        )



@extend_schema(
    tags=["cms"],
    summary="Get bookings page content",
    description=(
        "Returns all bookings page content: banner, booking steps, rates matrix, "
        "policies, and help strip. "
        "\n\n"
        "**NOT included in this response** (served by other endpoints):\n"
        "- Slot board (times, prices, statuses): `GET /api/v1/slots/date-wise/`\n"
        "- Calendar availability: computed from slots endpoint\n"
        "- Arena hours/address/phone: `GET /api/v1/futsal/`\n"
        "- Booking creation: `POST /api/v1/bookings/`"
    ),
    responses={200: BookingsPageSerializer},
)
class BookingsPageView(GenericAPIView):
    """
    Public API for bookings page content.
    
    GET: Returns structured content for the bookings page (public, cached)
    PATCH: Updates bookings page content (admin-only)
    """
    
    serializer_class = BookingsPageSerializer
    
    def get_permissions(self):
        """Public for GET, admin-only for PATCH."""
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdmin()]
    
    def get(self, request):
        """Retrieve complete bookings page content."""
        data = get_bookings_page_data()
        serializer = self.get_serializer(data)
        return success_response(
            data=serializer.data,
            message="Bookings page content retrieved successfully."
        )
    
    @extend_schema(
        summary="Update bookings page content",
        description="Updates bookings page content. Only modified fields need to be provided.",
        request=BookingsPageSerializer,
        responses={200: BookingsPageSerializer},
    )
    def patch(self, request):
        """Update bookings page content (admin-only)."""
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        updated_data = update_bookings_page_content(serializer.validated_data)
        response_serializer = self.get_serializer(updated_data)
        
        return success_response(
            data=response_serializer.data,
            message="Bookings page content updated successfully.",
            status=status.HTTP_200_OK
        )



@extend_schema(
    tags=["cms"],
    summary="Get gallery page content",
    description=(
        "Returns all gallery page content: header, category filters, photos masonry grid, "
        "video clips section, and closing CTA. "
        "\n\n"
        "**Frontend behavior** (not included in this response):\n"
        "- Category filtering: Client-side filtering by category key\n"
        "- Lightbox navigation: Previous/next, counters\n"
        "- Video player: Dialog with controls"
    ),
    responses={200: GalleryPageSerializer},
)
class GalleryPageView(GenericAPIView):
    """
    Public API for gallery page content.
    
    GET: Returns structured content for the gallery page (public, cached)
    PATCH: Updates gallery page content (admin-only)
    """
    
    serializer_class = GalleryPageSerializer
    
    def get_permissions(self):
        """Public for GET, admin-only for PATCH."""
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdmin()]
    
    def get(self, request):
        """Retrieve complete gallery page content."""
        data = get_gallery_page_data()
        serializer = self.get_serializer(data)
        return success_response(
            data=serializer.data,
            message="Gallery page content retrieved successfully."
        )
    
    @extend_schema(
        summary="Update gallery page content",
        description="Updates gallery page content. Only modified fields need to be provided.",
        request=GalleryPageSerializer,
        responses={200: GalleryPageSerializer},
    )
    def patch(self, request):
        """Update gallery page content (admin-only)."""
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        updated_data = update_gallery_page_content(serializer.validated_data)
        response_serializer = self.get_serializer(updated_data)
        
        return success_response(
            data=response_serializer.data,
            message="Gallery page content updated successfully.",
            status=status.HTTP_200_OK
        )



@extend_schema(
    tags=["cms"],
    summary="Get about page content",
    description=(
        "Returns all about page content in render order: "
        "Hero → Stats → Story & timeline → Values → Community & coaching → Team → CTA banner. "
        "\n\n"
        "Sections are fixed by design. Empty arrays hide their entire section gracefully."
    ),
    responses={200: AboutPageSerializer},
)
class AboutPageView(GenericAPIView):
    """
    Public API for about page content.
    
    GET: Returns structured content for the about page (public, cached)
    PATCH: Updates about page content (admin-only)
    """
    
    serializer_class = AboutPageSerializer
    
    def get_permissions(self):
        """Public for GET, admin-only for PATCH."""
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdmin()]
    
    def get(self, request):
        """Retrieve complete about page content."""
        data = get_about_page_data()
        serializer = self.get_serializer(data)
        return success_response(
            data=serializer.data,
            message="About page content retrieved successfully."
        )
    
    @extend_schema(
        summary="Update about page content",
        description="Updates about page content. Only modified fields need to be provided.",
        request=AboutPageSerializer,
        responses={200: AboutPageSerializer},
    )
    def patch(self, request):
        """Update about page content (admin-only)."""
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        updated_data = update_about_page_content(serializer.validated_data)
        response_serializer = self.get_serializer(updated_data)
        
        return success_response(
            data=response_serializer.data,
            message="About page content updated successfully.",
            status=status.HTTP_200_OK
        )



@extend_schema(
    tags=["cms"],
    summary="Get contact page content",
    description=(
        "Returns contact page presentation copy: form labels/placeholders, "
        "success messages, contact detail labels, and booking nudge card. "
        "\n\n"
        "**NOT included in this response** (served by other endpoints):\n"
        "- Actual address, phone, email, hours: `GET /api/v1/futsal/`\n"
        "- Form submission: `POST /api/v1/contact/`\n"
        "\n"
        "The CMS provides UI copy only. Frontend merges live contact values from /futsal/ endpoint."
    ),
    responses={200: ContactPageSerializer},
)
class ContactPageView(GenericAPIView):
    """
    Public API for contact page content.
    
    GET: Returns structured content for the contact page (public, cached)
    PATCH: Updates contact page content (admin-only)
    """
    
    serializer_class = ContactPageSerializer
    
    def get_permissions(self):
        """Public for GET, admin-only for PATCH."""
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdmin()]
    
    def get(self, request):
        """Retrieve complete contact page content."""
        data = get_contact_page_data()
        serializer = self.get_serializer(data)
        return success_response(
            data=serializer.data,
            message="Contact page content retrieved successfully."
        )
    
    @extend_schema(
        summary="Update contact page content",
        description="Updates contact page content. Only modified fields need to be provided.",
        request=ContactPageSerializer,
        responses={200: ContactPageSerializer},
    )
    def patch(self, request):
        """Update contact page content (admin-only)."""
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        updated_data = update_contact_page_content(serializer.validated_data)
        response_serializer = self.get_serializer(updated_data)
        
        return success_response(
            data=response_serializer.data,
            message="Contact page content updated successfully.",
            status=status.HTTP_200_OK
        )



# ============================================================================
# Gallery Media Management ViewSets
# ============================================================================

from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from cms.models import GalleryPhoto, GalleryVideo
from cms.serializers import (
    GalleryPhotoUploadSerializer,
    GalleryPhotoDetailSerializer,
    GalleryVideoUploadSerializer,
    GalleryVideoDetailSerializer,
)
from common.mixins import EnvelopeMixin
from django.core.cache import cache
import uuid


@extend_schema(tags=["cms"])
class GalleryPhotoViewSet(EnvelopeMixin, viewsets.ModelViewSet):
    """Manage CMS gallery photos with upload/update/delete operations."""
    
    permission_classes = [IsAuthenticated, IsAdmin]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = GalleryPhoto.objects.all()
    filterset_fields = ["category", "is_active"]
    ordering_fields = ["sort_order", "created_at"]
    ordering = ["sort_order", "created_at"]
    
    def get_serializer_class(self):
        """Return different serializers for upload vs. display."""
        if self.action in {"create", "update", "partial_update"}:
            return GalleryPhotoUploadSerializer
        return GalleryPhotoDetailSerializer
    
    @extend_schema(
        summary="List all gallery photos",
        description="Returns all gallery photos. Filter by category or is_active.",
        responses={200: GalleryPhotoDetailSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Upload a new gallery photo",
        description=(
            "Upload a new photo to the CMS gallery. "
            "Provide the image file and metadata (title, alt_text, category, etc.)."
        ),
        responses={201: GalleryPhotoDetailSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Generate unique key if not provided
        validated_data = serializer.validated_data
        if not validated_data.get('key'):
            validated_data['key'] = f"photo_{uuid.uuid4().hex[:8]}"
        
        # Create the photo
        photo = GalleryPhoto.objects.create(**validated_data)
        
        # Invalidate gallery cache
        cache.delete("cms:gallery:data")
        
        return success_response(
            data=GalleryPhotoDetailSerializer(photo).data,
            message="Gallery photo uploaded successfully.",
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Get gallery photo details",
        description="Returns details of a specific gallery photo.",
        responses={200: GalleryPhotoDetailSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update gallery photo",
        description=(
            "Update photo metadata or replace the image file. "
            "Only include fields you want to change."
        ),
        responses={200: GalleryPhotoDetailSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Update the photo
        for attr, value in serializer.validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Invalidate gallery cache
        cache.delete("cms:gallery:data")
        
        return success_response(
            data=GalleryPhotoDetailSerializer(instance).data,
            message="Gallery photo updated successfully."
        )
    
    @extend_schema(
        summary="Delete gallery photo",
        description="Deletes the gallery photo and removes the image from Cloudinary."
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        photo_id = str(instance.id)
        photo_title = instance.title
        
        # Delete the image file from storage (Cloudinary)
        if instance.image:
            instance.image.storage.delete(instance.image.name)
        
        # Delete the database record
        instance.delete()
        
        # Invalidate gallery cache
        cache.delete("cms:gallery:data")
        
        return success_response(
            data={"id": photo_id, "title": photo_title},
            message="Gallery photo deleted successfully.",
            status=status.HTTP_200_OK
        )


@extend_schema(tags=["cms"])
class GalleryVideoViewSet(EnvelopeMixin, viewsets.ModelViewSet):
    """Manage CMS gallery videos with upload/update/delete operations."""
    
    permission_classes = [IsAuthenticated, IsAdmin]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = GalleryVideo.objects.all()
    filterset_fields = ["category", "is_active"]
    ordering_fields = ["sort_order", "created_at"]
    ordering = ["sort_order", "created_at"]
    
    def get_serializer_class(self):
        """Return different serializers for upload vs. display."""
        if self.action in {"create", "update", "partial_update"}:
            return GalleryVideoUploadSerializer
        return GalleryVideoDetailSerializer
    
    @extend_schema(
        summary="List all gallery videos",
        description="Returns all gallery videos. Filter by category or is_active.",
        responses={200: GalleryVideoDetailSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Upload a new gallery video",
        description=(
            "Upload a new video to the CMS gallery. "
            "Provide the video file, poster image, and metadata (title, category, duration, etc.)."
        ),
        responses={201: GalleryVideoDetailSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Generate unique key if not provided
        validated_data = serializer.validated_data
        if not validated_data.get('key'):
            validated_data['key'] = f"video_{uuid.uuid4().hex[:8]}"
        
        # Create the video
        video = GalleryVideo.objects.create(**validated_data)
        
        # Invalidate gallery cache
        cache.delete("cms:gallery:data")
        
        return success_response(
            data=GalleryVideoDetailSerializer(video).data,
            message="Gallery video uploaded successfully.",
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Get gallery video details",
        description="Returns details of a specific gallery video.",
        responses={200: GalleryVideoDetailSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update gallery video",
        description=(
            "Update video metadata, replace the video file, or update the poster image. "
            "Only include fields you want to change."
        ),
        responses={200: GalleryVideoDetailSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Update the video
        for attr, value in serializer.validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Invalidate gallery cache
        cache.delete("cms:gallery:data")
        
        return success_response(
            data=GalleryVideoDetailSerializer(instance).data,
            message="Gallery video updated successfully."
        )
    
    @extend_schema(
        summary="Delete gallery video",
        description="Deletes the gallery video and removes files (video + poster) from Cloudinary."
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        video_id = str(instance.id)
        video_title = instance.title
        
        # Delete the video file from storage (Cloudinary)
        if instance.video:
            instance.video.storage.delete(instance.video.name)
        
        # Delete the poster image from storage (Cloudinary)
        if instance.poster:
            instance.poster.storage.delete(instance.poster.name)
        
        # Delete the database record
        instance.delete()
        
        # Invalidate gallery cache
        cache.delete("cms:gallery:data")
        
        return success_response(
            data={"id": video_id, "title": video_title},
            message="Gallery video deleted successfully.",
            status=status.HTTP_200_OK
        )
