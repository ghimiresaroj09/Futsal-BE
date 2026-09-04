from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from accounts.models import OTP, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ["-created_at"]
    list_display = ["email", "full_name", "phone_number", "role", "is_verified", "is_active"]
    list_filter = ["role", "is_verified", "is_active"]
    search_fields = ["email", "full_name", "phone_number"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal", {"fields": ("full_name", "phone_number", "profile_image")}),
        ("Permissions", {"fields": ("role", "is_active", "is_verified", "is_staff",
                                     "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",),
                "fields": ("email", "full_name", "phone_number", "password1", "password2")}),
    )


admin.site.register(OTP)
