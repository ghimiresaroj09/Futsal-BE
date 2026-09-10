"""CMS URL configuration."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from cms.views import (
    AboutPageView,
    BookingsPageView,
    ContactPageView,
    GalleryPageView,
    HomepageView,
    GalleryPhotoViewSet,
    GalleryVideoViewSet,
)

# Router for gallery media management
gallery_router = DefaultRouter()
gallery_router.register(r'gallery/photos', GalleryPhotoViewSet, basename='cms-gallery-photos')
gallery_router.register(r'gallery/videos', GalleryVideoViewSet, basename='cms-gallery-videos')

urlpatterns = [
    # Page content endpoints
    path("homepage/", HomepageView.as_view(), name="cms-homepage"),
    path("bookings/", BookingsPageView.as_view(), name="cms-bookings"),
    path("gallery/", GalleryPageView.as_view(), name="cms-gallery"),
    path("about/", AboutPageView.as_view(), name="cms-about"),
    path("contact/", ContactPageView.as_view(), name="cms-contact"),
    
    # Gallery media management endpoints
    path("", include(gallery_router.urls)),
]
