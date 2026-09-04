"""Role based access control tests."""
import pytest

pytestmark = pytest.mark.django_db

ADMIN_URLS = [
    "/api/v1/admin/futsal/",
    "/api/v1/admin/reminders/",
    "/api/v1/admin/slots/",
    "/api/v1/admin/bookings/",
    "/api/v1/admin/dashboard/",
    "/api/v1/analytics/",
    "/api/v1/admin/contact/",
    "/api/v1/admin/users/",
    "/api/v1/admin/profile/",
]


@pytest.mark.parametrize("url", ADMIN_URLS)
def test_normal_user_gets_403_on_admin_endpoints(user_client, url):
    assert user_client.get(url).status_code == 403


@pytest.mark.parametrize("url", ADMIN_URLS)
def test_unauthenticated_gets_401(api, url):
    assert api.get(url).status_code == 401


@pytest.mark.parametrize("url", ADMIN_URLS)
def test_admin_can_access_admin_endpoints(admin_client, url):
    assert admin_client.get(url).status_code == 200


def test_admin_user_list_excludes_admins(admin_client, user, other_user, admin_user):
    response = admin_client.get("/api/v1/admin/users/")

    assert response.status_code == 200
    emails = {item["email"] for item in response.data["data"]["results"]}
    assert emails == {user.email, other_user.email}
    assert admin_user.email not in emails


def test_user_cannot_access_other_users_booking(api, other_user, booking):
    from accounts.services import issue_tokens

    api.credentials(HTTP_AUTHORIZATION=f"Bearer {issue_tokens(other_user)['access']}")
    assert api.get(f"/api/v1/bookings/{booking.id}/").status_code == 404


def test_users_cannot_modify_slots(user_client, slot):
    assert user_client.patch(f"/api/v1/slots/{slot.id}/", {"status": "BLOCKED"},
                             format="json").status_code == 405
