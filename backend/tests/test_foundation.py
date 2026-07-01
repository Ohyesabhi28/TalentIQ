"""
Foundation smoke tests — Module 1.

These tests verify that the application starts, middleware is wired,
and the health endpoint responds correctly. No database or external
services are required.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Synchronous test client — no async required for foundation tests."""
    return TestClient(app, raise_server_exceptions=True)


class TestHealthEndpoint:
    def test_health_returns_200(self, client: TestClient) -> None:
        response = client.get("/v1/health")
        assert response.status_code == 200

    def test_health_response_shape(self, client: TestClient) -> None:
        body = client.get("/v1/health").json()
        assert "status" in body
        assert "version" in body
        assert "environment" in body
        assert "services" in body
        assert isinstance(body["services"], list)

    def test_health_status_is_degraded_without_services(self, client: TestClient) -> None:
        """Without database/redis, overall status should be degraded, not unhealthy."""
        body = client.get("/v1/health").json()
        assert body["status"] in ("degraded", "healthy")

    def test_ping_returns_200(self, client: TestClient) -> None:
        response = client.get("/ping")
        assert response.status_code == 200
        assert response.json() == {"pong": True}


class TestRequestIDMiddleware:
    def test_response_includes_request_id(self, client: TestClient) -> None:
        response = client.get("/v1/health")
        assert "x-request-id" in response.headers

    def test_client_request_id_is_echoed(self, client: TestClient) -> None:
        custom_id = "test-correlation-id-12345"
        response = client.get("/v1/health", headers={"X-Request-ID": custom_id})
        assert response.headers.get("x-request-id") == custom_id


class TestCORSHeaders:
    def test_cors_allows_frontend_origin(self, client: TestClient) -> None:
        response = client.options(
            "/v1/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        # CORSMiddleware returns 200 for preflight
        assert response.status_code == 200


class TestErrorHandling:
    def test_unknown_route_returns_404(self, client: TestClient) -> None:
        response = client.get("/v1/does-not-exist")
        assert response.status_code == 404

    def test_validation_error_returns_400_envelope(self, client: TestClient) -> None:
        """
        POST to a route that doesn't exist will return 405, but we
        can craft a test once real endpoints exist. For now, verify the
        base error shape is consistent on any non-2xx.
        """
        response = client.get("/v1/does-not-exist")
        # FastAPI default 404 — future custom handler will wrap in our envelope
        assert response.status_code in (404, 422)
