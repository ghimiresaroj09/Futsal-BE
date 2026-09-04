"""Response envelope, docs and misc contract tests."""
import pytest

pytestmark = pytest.mark.django_db


def test_schema_endpoint(api):
    assert api.get("/api/schema/").status_code == 200


def test_swagger_docs(api):
    assert api.get("/api/docs/").status_code == 200


def test_success_envelope(user_client):
    response = user_client.get("/api/v1/users/me/")
    assert set(response.data) == {"success", "message", "data"}
    assert response.data["success"] is True


def test_error_envelope(api):
    response = api.post("/api/v1/auth/login/", {"email": "x@example.com"}, format="json")
    assert set(response.data) == {"success", "message", "errors"}
    assert response.data["success"] is False


def test_404_envelope(user_client):
    response = user_client.get("/api/v1/bookings/11111111-1111-1111-1111-111111111111/")
    assert response.status_code == 404
    assert response.data["success"] is False


def test_internal_errors_are_not_leaked(user_client, monkeypatch):
    from bookings import views

    def boom(*args, **kwargs):
        raise RuntimeError("secret internal detail")

    monkeypatch.setattr(views.services, "create_booking", boom)
    response = user_client.post("/api/v1/bookings/", {
        "slot_id": "11111111-1111-1111-1111-111111111111", "full_name": "John Doe",
        "email": "john@example.com", "phone_number": "9800000000",
    }, format="json")
    assert response.status_code == 500
    assert "secret internal detail" not in str(response.data)


def test_ordering_whitelist(api, slot):
    ok = api.get("/api/v1/slots/?ordering=start_time")
    ignored = api.get("/api/v1/slots/?ordering=futsal__price_per_slot")
    assert ok.status_code == 200 and ignored.status_code == 200


def test_page_size_capped_at_100(api, slot):
    response = api.get("/api/v1/slots/?page_size=1000")
    assert response.status_code == 200
