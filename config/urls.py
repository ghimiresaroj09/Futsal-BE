"""Root URL configuration (API v1)."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView,
)
from drf_spectacular.renderers import OpenApiJsonRenderer
from rest_framework.routers import DefaultRouter

from accounts.urls import auth_urlpatterns, user_urlpatterns
from bookings.views import BookingViewSet
from contact.views import ContactCreateViewSet
from futsal.views import FutsalDetailView, PublicFutsalMediaViewSet, PublicSlotViewSet

router = DefaultRouter()
router.register("slots", PublicSlotViewSet, basename="slot")
router.register("bookings", BookingViewSet, basename="booking")
router.register("contact", ContactCreateViewSet, basename="contact")
router.register("futsal-media", PublicFutsalMediaViewSet, basename="futsal-media")

api_v1 = [
    path("auth/", include((auth_urlpatterns, "auth"))),
    path("users/", include((user_urlpatterns, "users"))),
    path("futsal/", FutsalDetailView.as_view(), name="futsal"),
    path("admin/", include("config.admin_urls")),
    path("", include(router.urls)),
]

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api/v1/", include((api_v1, "v1"))),
    path(
        "api/schema/",
        SpectacularAPIView.as_view(renderer_classes=[OpenApiJsonRenderer]),
        name="schema",
    ),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
