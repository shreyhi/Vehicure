import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.database.init_db import init_db

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    loop = asyncio.get_event_loop_policy().get_event_loop()
    loop.run_until_complete(init_db())

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["product"] == "Vehicure"

def test_fleet_overview_endpoint():
    response = client.get("/api/fleet/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_vehicles" in data
    assert "healthy_vehicles" in data

def test_fleet_vehicles_endpoint():
    response = client.get("/api/fleet/vehicles?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_health_summary_endpoint():
    response = client.get("/api/health/summary")
    assert response.status_code == 200

def test_alerts_endpoint():
    response = client.get("/api/alerts")
    assert response.status_code == 200

def test_analytics_endpoint():
    response = client.get("/api/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "model_performance" in data

def test_system_health_endpoint():
    response = client.get("/api/system/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["HEALTHY", "DEGRADED"]

def test_simulator_status_endpoint():
    response = client.get("/api/simulator/status")
    assert response.status_code == 200
