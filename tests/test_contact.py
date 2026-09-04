"""Contact-us tests."""
import pytest

from common.enums import ContactStatus
from contact.models import ContactMessage

pytestmark = pytest.mark.django_db

URL = "/api/v1/contact/"
ADMIN_URL = "/api/v1/admin/contact/"

PAYLOAD = {
    "name": "Jane Doe", "email": "jane@example.com", "phone_number": "9800000066",
    "subject": "Ground availability", "message": "Do you have slots this weekend?",
}


def test_anyone_can_submit_contact_message(api):
    response = api.post(URL, PAYLOAD, format="json")
    assert response.status_code == 201
    assert response.data["data"]["status"] == ContactStatus.NEW


def test_contact_validation(api):
    response = api.post(URL, {**PAYLOAD, "email": "bad", "phone_number": "abc"},
                        format="json")
    assert response.status_code == 400
    assert "email" in response.data["errors"]
    assert "phone_number" in response.data["errors"]


def test_contact_requires_all_fields(api):
    response = api.post(URL, {"name": "Jane Doe"}, format="json")
    assert response.status_code == 400
    assert "message" in response.data["errors"]


def test_admin_can_list_and_retrieve(admin_client, api):
    api.post(URL, PAYLOAD, format="json")
    message = ContactMessage.objects.get()
    assert admin_client.get(ADMIN_URL).data["data"]["count"] == 1
    detail = admin_client.get(f"{ADMIN_URL}{message.id}/")
    assert detail.data["data"]["subject"] == PAYLOAD["subject"]


def test_admin_can_update_status(admin_client, api):
    api.post(URL, PAYLOAD, format="json")
    message = ContactMessage.objects.get()
    response = admin_client.patch(f"{ADMIN_URL}{message.id}/",
                                  {"status": ContactStatus.RESOLVED,
                                   "admin_notes": "Called back"}, format="json")
    assert response.status_code == 200
    message.refresh_from_db()
    assert message.status == ContactStatus.RESOLVED


def test_normal_user_cannot_list_contacts(user_client):
    assert user_client.get(ADMIN_URL).status_code == 403
