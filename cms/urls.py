"""CMS URL configuration."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cms.views import (
    HeroSectionView,
    ArenaSectionView,
    WhyUsSectionView,
    CarouselImageViewSet,
    TestimonialViewSet,
    GalleryCategoryViewSet,
    GalleryImageViewSet,
    GalleryHighlightViewSet,
)

# Router for collections
router = DefaultRouter()
router.register(r'homepage/carousel', CarouselImageViewSet, basename='carousel')
router.register(r'testimonials', TestimonialViewSet, basename='testimonial')
router.register(r'gallery/category', GalleryCategoryViewSet, basename='gallery-category')
router.register(r'gallery/images', GalleryImageViewSet, basename='gallery-image')
router.register(r'gallery/highlights', GalleryHighlightViewSet, basename='gallery-highlight')

urlpatterns = [
    # Hero section
    path("homepage/hero-section/", HeroSectionView.as_view(), name="hero-section"),
    
    # Arena section
    path("homepage/arena/", ArenaSectionView.as_view(), name="arena-section"),
    
    # Why Us section
    path("homepage/why-us/", WhyUsSectionView.as_view(), name="why-us-section"),
    
    # Collections
    path("", include(router.urls)),
]
