from django.contrib import admin

from contact.models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["subject", "name", "email", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["name", "email", "subject"]
