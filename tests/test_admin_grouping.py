"""Admin API is grouped by domain, each with its own Swagger tag."""
import pytest

pytestmark = pytest.mark.django_db

EXPECTED_TAGS = {
    "admin-profile", "admin-futsal", "admin-slots", "admin-bookings",
    "admin-dashboard", "admin-contact", "admin-reminders", "analytics",
}


@pytest.fixture
def schema(api):
    return api.get("/api/schema/?format=json").data


def test_all_admin_groups_present(schema):
    tags = {tag for path in schema["paths"].values()
            for op in path.values() if isinstance(op, dict)
            for tag in op.get("tags", [])}
    assert EXPECTED_TAGS <= tags


def test_no_generic_admin_tag_remains(schema):
    tags = {tag for path in schema["paths"].values()
            for op in path.values() if isinstance(op, dict)
            for tag in op.get("tags", [])}
    assert "admin" not in tags


@pytest.mark.parametrize("prefix,tag", [
    ("/api/v1/admin/profile/", "admin-profile"),
    ("/api/v1/admin/futsal/", "admin-futsal"),
    ("/api/v1/admin/slots/", "admin-slots"),
    ("/api/v1/admin/bookings/", "admin-bookings"),
    ("/api/v1/admin/dashboard/", "admin-dashboard"),
    ("/api/v1/admin/contact/", "admin-contact"),
    ("/api/v1/admin/reminders/", "admin-reminders"),
])
def test_each_group_is_tagged_correctly(schema, prefix, tag):
    operations = schema["paths"][prefix]
    tags = {t for op in operations.values() if isinstance(op, dict)
            for t in op.get("tags", [])}
    assert tags == {tag}


def test_admin_reminder_history(admin_client, booking):
    admin_client.post(f"/api/v1/admin/bookings/{booking.id}/send-reminder/")
    response = admin_client.get("/api/v1/admin/reminders/")
    assert response.status_code == 200
    assert response.data["data"]["count"] == 1
    assert response.data["data"]["results"][0]["reminder_type"] == "MANUAL"


def test_reminder_filtering(admin_client, booking):
    admin_client.post(f"/api/v1/admin/bookings/{booking.id}/send-reminder/")
    assert admin_client.get(
        "/api/v1/admin/reminders/?status=SENT").data["data"]["count"] == 1
    assert admin_client.get(
        "/api/v1/admin/reminders/?status=FAILED").data["data"]["count"] == 0
