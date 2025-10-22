import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] in ("healthy", "unhealthy")
    assert "service_status" in body
    assert "modelos_status" in body


def test_predict_ok(monkeypatch):
    # Mockear el servicio para evitar cargar modelos reales
    class DummyService:
        def predecir_precio(self, request):
            return 12345.67

    from backend.api.dependencies import get_car_prediction_service

    def fake_dep():
        return DummyService()

    app.dependency_overrides[get_car_prediction_service] = fake_dep

    payload = {
        "Manufacturer": "Toyota",
        "Model": "Camry",
        "Year": 2022,
        "Transmission": "Automatic",
        "Mileage": 15000,
        "FuelType": "Petrol",
        "EngineSize": 2.5,
    }
    resp = client.post("/predict", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "success"
    assert body["data"]["predicted_price"] == 12345.67

    # Limpiar override
    app.dependency_overrides.clear()
