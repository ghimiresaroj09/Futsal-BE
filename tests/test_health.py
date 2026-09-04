"""Health check endpoint used by Render's health probe."""
from __future__ import annotations

from unittest import mock

import pytest

pytestmark = pytest.mark.django_db

URL = "/healthz/"


def test_health_returns_200(api):
    response = api.get(URL)
    assert response.status_code == 200
    assert response.data["data"] == {"status": "ok", "database": "ok"}


def test_health_needs_no_authentication(api):
    assert api.get(URL).status_code == 200


def test_health_returns_503_when_database_is_down(api):
    with mock.patch("common.health_views.connection") as conn:
        conn.cursor.side_effect = Exception("connection refused")
        response = api.get(URL)
    assert response.status_code == 503
    assert response.data["success"] is False
    assert "database" in response.data["errors"]
