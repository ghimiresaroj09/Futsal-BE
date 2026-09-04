from django.contrib import admin

from notifications.models import AdminNotification, Reminder

admin.site.register(Reminder)
admin.site.register(AdminNotification)
