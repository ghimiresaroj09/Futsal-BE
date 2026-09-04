from django.db import migrations
from django.contrib.auth.hashers import make_password


ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "Admin@12345"
ADMIN_PHONE = "9800000001"


def seed_admin(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    admin, created = User.objects.get_or_create(
        email=ADMIN_EMAIL,
        defaults={
            "full_name": "Futsal Admin",
            "phone_number": ADMIN_PHONE,
            "role": "ADMIN",
            "is_active": True,
            "is_verified": True,
            "is_staff": True,
            "is_superuser": True,
        },
    )
    if created:
        admin.password = make_password(ADMIN_PASSWORD)
        admin.save(update_fields=["password"])
    else:
        admin.full_name = "Futsal Admin"
        admin.role = "ADMIN"
        admin.is_active = True
        admin.is_verified = True
        admin.is_staff = True
        admin.is_superuser = True
        admin.password = make_password(ADMIN_PASSWORD)
        admin.save()


def remove_admin(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.filter(email=ADMIN_EMAIL).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_admin, remove_admin),
    ]
