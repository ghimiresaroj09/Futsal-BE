"""User profile tests."""
import pytest

pytestmark = pytest.mark.django_db

ME_URL = "/api/v1/users/me/"


def test_get_profile(user_client, user):
    response = user_client.get(ME_URL)
    assert response.status_code == 200
    assert response.data["data"]["email"] == user.email


def test_profile_requires_authentication(api):
    assert api.get(ME_URL).status_code == 401


def test_update_profile(user_client):
    response = user_client.patch(ME_URL, {"full_name": "Updated Name"}, format="json")
    assert response.status_code == 200
    assert response.data["data"]["full_name"] == "Updated Name"


def test_profile_email_uniqueness(user_client, other_user):
    response = user_client.patch(ME_URL, {"email": other_user.email}, format="json")
    assert response.status_code == 400


def test_profile_phone_uniqueness(user_client, other_user):
    response = user_client.patch(ME_URL, {"phone_number": other_user.phone_number},
                                 format="json")
    assert response.status_code == 400


def test_email_change_requires_reverification(user_client, user):
    user_client.patch(ME_URL, {"email": "changed@example.com"}, format="json")
    user.refresh_from_db()
    assert user.email == "changed@example.com"
    assert user.is_verified is False
