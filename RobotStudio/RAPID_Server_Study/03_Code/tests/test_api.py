from fastapi.testclient import TestClient

from abb_bridge.config import BridgeSettings
from abb_bridge.main import create_app


def make_client() -> TestClient:
    app = create_app(
        BridgeSettings(api_key="test-key", start_tcp_gateway=False, controller_mode="mock")
    )
    return TestClient(app)


def test_health_is_public() -> None:
    with make_client() as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_status_requires_key() -> None:
    with make_client() as client:
        response = client.get("/v1/status")
    assert response.status_code == 401


def test_command_round_trip() -> None:
    with make_client() as client:
        response = client.post(
            "/v1/commands",
            headers={"X-Bridge-Key": "test-key"},
            json={"id": "api-1", "type": "ping", "payload": {}},
        )
    assert response.status_code == 200
    assert response.json()["payload"]["message"] == "pong"

