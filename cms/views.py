"""CMS views for testimonials."""
from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from cms.models import (
    HeroSection,
    CarouselImage,
    Testimonial,
    ArenaSection,
    WhyUsSection,
    GalleryCategory,
    GalleryImage,
    GalleryHighlight,
)
from cms.serializers import (
    HeroSectionSerializer,
    HeroSectionUpdateSerializer,
    CarouselImageSerializer,
    CarouselImageUploadSerializer,
    TestimonialSerializer,
    TestimonialUploadSerializer,
    ArenaSectionSerializer,
    ArenaSectionUpdateSerializer,
    WhyUsSectionSerializer,
    WhyUsSectionUpdateSerializer,
    GalleryCategorySerializer,
    GalleryCategoryCreateUpdateSerializer,
    GalleryImageSerializer,
    GalleryImageUploadSerializer,
    GalleryHighlightSerializer,
    GalleryHighlightUploadSerializer,
)
from common.mixins import EnvelopeMixin
from common.permissions import IsAdmin
from common.responses import success_response


@extend_schema(tags=["cms"])
class HeroSectionView(APIView):
    """Manage homepage hero section (singleton)."""
    
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_permissions(self):
        """Public can view, only admins can update."""
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsAdmin()]
    
    @extend_schema(
        summary="Get hero section content",
        description="Returns the homepage hero section content including title, description, image, and stats.",
        responses={200: HeroSectionSerializer}
    )
    def get(self, request):
        """Get hero section content."""
        hero = HeroSection.get_solo()
        serializer = HeroSectionSerializer(hero)
        return success_response(
            data=serializer.data,
            message="Hero section retrieved successfully."
        )
    
    @extend_schema(
        summary="Update hero section content",
        description="Update hero section content. Only include fields you want to change. Admin only.",
        request=HeroSectionUpdateSerializer,
        responses={200: HeroSectionSerializer}
    )
    def patch(self, request):
        """Update hero section content."""
        hero = HeroSection.get_solo()
        serializer = HeroSectionUpdateSerializer(hero, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Return updated data with display serializer
        return success_response(
            data=HeroSectionSerializer(hero).data,
            message="Hero section updated successfully."
        )


@extend_schema(tags=["cms"])
class CarouselImageViewSet(EnvelopeMixin, viewsets.ModelViewSet):
    """Manage homepage carousel images."""
    
    queryset = CarouselImage.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ["is_active"]
    ordering_fields = ["sort_order", "created_at"]
    ordering = ["sort_order", "created_at"]
    
    def get_permissions(self):
        """Public can view, only admins can create/update/delete."""
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsAdmin()]
    
    def get_serializer_class(self):
        """Use upload serializer for create/update, display serializer for read."""
        if self.action in ["create", "update", "partial_update"]:
            return CarouselImageUploadSerializer
        return CarouselImageSerializer
    
    def get_queryset(self):
        """Filter active carousel images for public, show all for admins."""
        queryset = super().get_queryset()
        
        # For public (list/retrieve), only show active images
        if self.action in ["list", "retrieve"]:
            request = self.request
            is_admin = (
                request and 
                request.user and 
                request.user.is_authenticated and 
                hasattr(request.user, 'role') and
                request.user.role == 'ADMIN'
            )
            
            if not is_admin:
                queryset = queryset.filter(is_active=True)
        
        return queryset
    
    @extend_schema(
        summary="List all carousel images",
        description="Returns all active carousel images. Admins see all images including inactive ones.",
        responses={200: CarouselImageSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Upload carousel image",
        description="Upload a new carousel image. Admin only.",
        responses={201: CarouselImageSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        carousel = serializer.save()
        
        return success_response(
            data=CarouselImageSerializer(carousel).data,
            message="Carousel image uploaded successfully.",
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Get carousel image details",
        description="Returns details of a specific carousel image.",
        responses={200: CarouselImageSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update carousel image",
        description="Update carousel image or metadata. Admin only.",
        responses={200: CarouselImageSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        carousel = serializer.save()
        
        return success_response(
            data=CarouselImageSerializer(carousel).data,
            message="Carousel image updated successfully."
        )
    
    @extend_schema(
        summary="Delete carousel image",
        description="Deletes the carousel image and removes it from Cloudinary. Admin only."
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        carousel_id = str(instance.id)
        alt_text = instance.alt_text
        
        # Delete the image file from storage (Cloudinary)
        if instance.image:
            try:
                instance.image.storage.delete(instance.image.name)
            except Exception:
                pass  # Continue even if file deletion fails
        
        # Delete the database record
        instance.delete()
        
        return success_response(
            data={"id": carousel_id, "alt_text": alt_text},
            message="Carousel image deleted successfully.",
            status=status.HTTP_200_OK
        )


@extend_schema(tags=["testimonials"])
class TestimonialViewSet(EnvelopeMixin, viewsets.ModelViewSet):
    """Manage customer testimonials."""
    
    queryset = Testimonial.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ["is_active"]
    ordering_fields = ["sort_order", "created_at"]
    ordering = ["sort_order", "-created_at"]
    
    def get_permissions(self):
        """Public can view, only admins can create/update/delete."""
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsAdmin()]
    
    def get_serializer_class(self):
        """Use upload serializer for create/update, display serializer for read."""
        if self.action in ["create", "update", "partial_update"]:
            return TestimonialUploadSerializer
        return TestimonialSerializer
    
    def get_queryset(self):
        """Filter active testimonials for public, show all for admins."""
        queryset = super().get_queryset()
        
        # For public (list/retrieve), only show active testimonials
        if self.action in ["list", "retrieve"]:
            request = self.request
            is_admin = (
                request and 
                request.user and 
                request.user.is_authenticated and 
                hasattr(request.user, 'role') and
                request.user.role == 'ADMIN'
            )
            
            if not is_admin:
                queryset = queryset.filter(is_active=True)
        
        return queryset
    
    @extend_schema(
        summary="List all testimonials",
        description="Returns all active testimonials. Admins see all testimonials including inactive ones.",
        responses={200: TestimonialSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create a new testimonial",
        description="Upload a customer testimonial with optional image. Admin only.",
        responses={201: TestimonialSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        testimonial = serializer.save()
        
        return success_response(
            data=TestimonialSerializer(testimonial).data,
            message="Testimonial created successfully.",
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Get testimonial details",
        description="Returns details of a specific testimonial.",
        responses={200: TestimonialSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update testimonial",
        description="Update testimonial details or replace the image. Admin only.",
        responses={200: TestimonialSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        testimonial = serializer.save()
        
        return success_response(
            data=TestimonialSerializer(testimonial).data,
            message="Testimonial updated successfully."
        )
    
    @extend_schema(
        summary="Delete testimonial",
        description="Deletes the testimonial and removes the image from Cloudinary. Admin only."
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        testimonial_id = str(instance.id)
        full_name = instance.full_name
        
        # Delete the image file from storage (Cloudinary)
        if instance.image:
            try:
                instance.image.storage.delete(instance.image.name)
            except Exception:
                pass  # Continue even if file deletion fails
        
        # Delete the database record
        instance.delete()
        
        return success_response(
            data={"id": testimonial_id, "full_name": full_name},
            message="Testimonial deleted successfully.",
            status=status.HTTP_200_OK
        )



@extend_schema(tags=["cms"])
class ArenaSectionView(APIView):
    """Manage homepage arena section (singleton)."""
    
    parser_classes = [JSONParser]
    
    def get_permissions(self):
        """Public can view, only admins can update."""
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsAdmin()]
    
    @extend_schema(
        summary="Get arena section content",
        description="Returns the homepage arena section content including title, description, and features array.",
        responses={200: ArenaSectionSerializer}
    )
    def get(self, request):
        """Get arena section content."""
        arena = ArenaSection.get_solo()
        serializer = ArenaSectionSerializer(arena)
        return success_response(
            data=serializer.data,
            message="Arena section retrieved successfully."
        )
    
    @extend_schema(
        summary="Update arena section content",
        description="Update arena section content. Only include fields you want to change. Admin only.",
        request=ArenaSectionUpdateSerializer,
        responses={200: ArenaSectionSerializer}
    )
    def patch(self, request):
        """Update arena section content."""
        arena = ArenaSection.get_solo()
        serializer = ArenaSectionUpdateSerializer(arena, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Return updated data with display serializer
        return success_response(
            data=ArenaSectionSerializer(arena).data,
            message="Arena section updated successfully."
        )



@extend_schema(tags=["cms"])
class WhyUsSectionView(APIView):
    """Manage homepage why us section (singleton)."""
    
    parser_classes = [JSONParser]
    
    def get_permissions(self):
        """Public can view, only admins can update."""
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsAdmin()]
    
    @extend_schema(
        summary="Get why us section content",
        description="Returns the homepage why us section content including title, description, and features array with objects.",
        responses={200: WhyUsSectionSerializer}
    )
    def get(self, request):
        """Get why us section content."""
        why_us = WhyUsSection.get_solo()
        serializer = WhyUsSectionSerializer(why_us)
        return success_response(
            data=serializer.data,
            message="Why us section retrieved successfully."
        )
    
    @extend_schema(
        summary="Update why us section content",
        description="Update why us section content. Only include fields you want to change. Admin only.",
        request=WhyUsSectionUpdateSerializer,
        responses={200: WhyUsSectionSerializer}
    )
    def patch(self, request):
        """Update why us section content."""
        why_us = WhyUsSection.get_solo()
        serializer = WhyUsSectionUpdateSerializer(why_us, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Return updated data with display serializer
        return success_response(
            data=WhyUsSectionSerializer(why_us).data,
            message="Why us section updated successfully."
        )



@extend_schema(tags=["cms"])
class GalleryCategoryViewSet(EnvelopeMixin, viewsets.ModelViewSet):
    """Manage gallery categories."""
    
    queryset = GalleryCategory.objects.all()
    parser_classes = [JSONParser]
    filterset_fields = ["is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["sort_order", "name", "created_at"]
    ordering = ["sort_order", "name"]
    
    def get_permissions(self):
        """Public can view, only admins can create/update/delete."""
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsAdmin()]
    
    def get_serializer_class(self):
        """Use create/update serializer for write operations."""
        if self.action in ["create", "update", "partial_update"]:
            return GalleryCategoryCreateUpdateSerializer
        return GalleryCategorySerializer
    
    def get_queryset(self):
        """Filter active categories for public, show all for admins."""
        queryset = super().get_queryset()
        
        # For public (list/retrieve), only show active categories
        if self.action in ["list", "retrieve"]:
            request = self.request
            is_admin = (
                request and 
                request.user and 
                request.user.is_authenticated and 
                hasattr(request.user, 'role') and
                request.user.role == 'ADMIN'
            )
            
            if not is_admin:
                queryset = queryset.filter(is_active=True)
        
        return queryset
    
    @extend_schema(
        summary="List all gallery categories",
        description="Returns all active gallery categories. Admins see all categories including inactive ones.",
        responses={200: GalleryCategorySerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create gallery category",
        description="Create a new gallery category. Admin only.",
        responses={201: GalleryCategorySerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()
        
        return success_response(
            data=GalleryCategorySerializer(category).data,
            message="Gallery category created successfully.",
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Get gallery category details",
        description="Returns details of a specific gallery category.",
        responses={200: GalleryCategorySerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update gallery category",
        description="Update gallery category details. Admin only.",
        responses={200: GalleryCategorySerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        category = self.get_object()
        serializer = self.get_serializer(category, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return success_response(
            data=GalleryCategorySerializer(category).data,
            message="Gallery category updated successfully."
        )
    
    @extend_schema(
        summary="Delete gallery category",
        description="Delete a gallery category. Admin only.",
        responses={200: None}
    )
    def destroy(self, request, *args, **kwargs):
        category = self.get_object()
        category_name = category.name
        category_id = str(category.id)
        category.delete()
        
        return success_response(
            data={"id": category_id, "name": category_name},
            message="Gallery category deleted successfully.",
            status=status.HTTP_200_OK
        )



@extend_schema(tags=["cms"])
class GalleryImageViewSet(EnvelopeMixin, viewsets.ModelViewSet):
    """Manage gallery images."""
    
    queryset = GalleryImage.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ["is_active", "category"]
    search_fields = ["title", "alt_text"]
    ordering_fields = ["sort_order", "title", "created_at", "category"]
    ordering = ["category", "sort_order", "created_at"]
    
    def get_permissions(self):
        """Public can view, only admins can create/update/delete."""
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsAdmin()]
    
    def get_serializer_class(self):
        """Use upload serializer for write operations."""
        if self.action in ["create", "update", "partial_update"]:
            return GalleryImageUploadSerializer
        return GalleryImageSerializer
    
    def get_queryset(self):
        """Filter active images for public, show all for admins."""
        queryset = super().get_queryset().select_related('category')
        
        # For public (list/retrieve), only show active images from active categories
        if self.action in ["list", "retrieve"]:
            request = self.request
            is_admin = (
                request and 
                request.user and 
                request.user.is_authenticated and 
                hasattr(request.user, 'role') and
                request.user.role == 'ADMIN'
            )
            
            if not is_admin:
                queryset = queryset.filter(
                    is_active=True,
                    category__is_active=True
                )
        
        return queryset
    
    @extend_schema(
        summary="List all gallery images",
        description="Returns all active gallery images. Admins see all images including inactive ones. Can filter by category.",
        responses={200: GalleryImageSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Upload gallery image",
        description="Upload a new gallery image to Cloudinary. Admin only.",
        responses={201: GalleryImageSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image = serializer.save()
        
        return success_response(
            data=GalleryImageSerializer(image).data,
            message="Gallery image uploaded successfully.",
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Get gallery image details",
        description="Returns details of a specific gallery image.",
        responses={200: GalleryImageSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update gallery image",
        description="Update gallery image or metadata. Admin only.",
        responses={200: GalleryImageSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        image = self.get_object()
        serializer = self.get_serializer(image, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return success_response(
            data=GalleryImageSerializer(image).data,
            message="Gallery image updated successfully."
        )
    
    @extend_schema(
        summary="Delete gallery image",
        description="Delete a gallery image. Admin only.",
        responses={200: None}
    )
    def destroy(self, request, *args, **kwargs):
        image = self.get_object()
        image_title = image.title
        image_id = str(image.id)
        image.delete()
        
        return success_response(
            data={"id": image_id, "title": image_title},
            message="Gallery image deleted successfully.",
            status=status.HTTP_200_OK
        )



@extend_schema(tags=["cms"])
class GalleryHighlightViewSet(EnvelopeMixin, viewsets.ModelViewSet):
    """Manage gallery highlight videos."""
    
    queryset = GalleryHighlight.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ["is_active"]
    search_fields = ["title", "tags"]
    ordering_fields = ["sort_order", "title", "created_at"]
    ordering = ["sort_order", "-created_at"]
    
    def get_permissions(self):
        """Public can view, only admins can create/update/delete."""
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsAdmin()]
    
    def get_serializer_class(self):
        """Use upload serializer for write operations."""
        if self.action in ["create", "update", "partial_update"]:
            return GalleryHighlightUploadSerializer
        return GalleryHighlightSerializer
    
    def get_queryset(self):
        """Filter active highlights for public, show all for admins."""
        queryset = super().get_queryset()
        
        # For public (list/retrieve), only show active highlights
        if self.action in ["list", "retrieve"]:
            request = self.request
            is_admin = (
                request and 
                request.user and 
                request.user.is_authenticated and 
                hasattr(request.user, 'role') and
                request.user.role == 'ADMIN'
            )
            
            if not is_admin:
                queryset = queryset.filter(is_active=True)
        
        return queryset
    
    @extend_schema(
        summary="List all gallery highlights",
        description="Returns all active gallery highlight videos. Admins see all highlights including inactive ones.",
        responses={200: GalleryHighlightSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Upload gallery highlight video",
        description="Upload a new highlight video to Cloudinary. Admin only. Tags is a plain text field (e.g., 'goal, highlight, tournament')",
        request=GalleryHighlightUploadSerializer,
        responses={201: GalleryHighlightSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        highlight = serializer.save()
        
        return success_response(
            data=GalleryHighlightSerializer(highlight).data,
            message="Gallery highlight uploaded successfully.",
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Get gallery highlight details",
        description="Returns details of a specific gallery highlight.",
        responses={200: GalleryHighlightSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update gallery highlight",
        description="Update gallery highlight video or metadata. Admin only.",
        responses={200: GalleryHighlightSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        highlight = self.get_object()
        serializer = self.get_serializer(highlight, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return success_response(
            data=GalleryHighlightSerializer(highlight).data,
            message="Gallery highlight updated successfully."
        )
    
    @extend_schema(
        summary="Delete gallery highlight",
        description="Delete a gallery highlight. Admin only.",
        responses={200: None}
    )
    def destroy(self, request, *args, **kwargs):
        highlight = self.get_object()
        highlight_title = highlight.title
        highlight_id = str(highlight.id)
        highlight.delete()
        
        return success_response(
            data={"id": highlight_id, "title": highlight_title},
            message="Gallery highlight deleted successfully.",
            status=status.HTTP_200_OK
        )
