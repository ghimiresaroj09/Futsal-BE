"""Admin API routing, grouped by domain.

Each group is mounted under its own prefix and documented under its own
Swagger tag:

    /api/v1/admin/profile/    → admin-profile
    /api/v1/admin/futsal/     → admin-futsal
    /api/v1/admin/slots/      → admin-slots
    /api/v1/admin/bookings/   → admin-bookings
    /api/v1/admin/revenue/    → admin-revenue
    /api/v1/admin/dashboard/  → admin-dashboard
    /api/v1/admin/contact/    → admin-contact
    /api/v1/admin/reminders/  → admin-reminders
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from accounts.views import AdminChangePasswordView, AdminProfileView, AdminUserViewSet
from bookings.views import AdminBookingViewSet
from contact.views import AdminContactViewSet
from dashboard import views as dashboard_views
from futsal.views import AdminFutsalMediaViewSet, AdminFutsalView, AdminSlotViewSet
from notifications.views import AdminNotificationViewSet, AdminReminderViewSet

# --- profile -----------------------------------------------------------------
profile_urls = [
    path("profile/", AdminProfileView.as_view(), name="admin-profile"),
    path("change-password/", AdminChangePasswordView.as_view(), name="admin-change-password"),
]

# --- futsal configuration ----------------------------------------------------
futsal_urls = [
    path("futsal/", AdminFutsalView.as_view(), name="admin-futsal"),
]

# --- slots -------------------------------------------------------------------
slot_router = DefaultRouter()
slot_router.register("slots", AdminSlotViewSet, basename="admin-slot")

# --- media -------------------------------------------------------------------
media_router = DefaultRouter()
media_router.register("media", AdminFutsalMediaViewSet, basename="admin-media")

# --- bookings ----------------------------------------------------------------
booking_router = DefaultRouter()
booking_router.register("bookings", AdminBookingViewSet, basename="admin-booking")

# --- contact -----------------------------------------------------------------
contact_router = DefaultRouter()
contact_router.register("contact", AdminContactViewSet, basename="admin-contact")

# --- reminders ---------------------------------------------------------------
reminder_router = DefaultRouter()
reminder_router.register("reminders", AdminReminderViewSet, basename="admin-reminder")

# --- in-app notifications ---------------------------------------------------
notification_router = DefaultRouter()
notification_router.register("notifications", AdminNotificationViewSet,
                             basename="admin-notification")

# --- users ------------------------------------------------------------------
user_router = DefaultRouter()
user_router.register("users", AdminUserViewSet, basename="admin-user")

# --- revenue -----------------------------------------------------------------
revenue_urls = [
    path("revenue/", dashboard_views.RevenueView.as_view(), name="admin-revenue"),
    path("revenue/daily/", dashboard_views.DailyRevenueView.as_view(),
         name="admin-revenue-daily"),
    path("revenue/weekly/", dashboard_views.WeeklyRevenueView.as_view(),
         name="admin-revenue-weekly"),
    path("revenue/monthly/", dashboard_views.MonthlyRevenueView.as_view(),
         name="admin-revenue-monthly"),
]

# --- dashboard ---------------------------------------------------------------
dashboard_urls = [
    path("dashboard/", dashboard_views.DashboardView.as_view(), name="admin-dashboard"),
    path("dashboard/revenue/", dashboard_views.DashboardRevenueView.as_view(),
         name="admin-dashboard-revenue"),
    path("dashboard/bookings/", dashboard_views.DashboardBookingsView.as_view(),
         name="admin-dashboard-bookings"),
    path("dashboard/slots/", dashboard_views.DashboardSlotsView.as_view(),
         name="admin-dashboard-slots"),
]

urlpatterns = [
    *profile_urls,
    *futsal_urls,
    *revenue_urls,
    *dashboard_urls,
    path("", include(media_router.urls)),
    path("", include(slot_router.urls)),
    path("", include(booking_router.urls)),
    path("", include(contact_router.urls)),
    path("", include(reminder_router.urls)),
    path("", include(notification_router.urls)),
    path("", include(user_router.urls)),
]
