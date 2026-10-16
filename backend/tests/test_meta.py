def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_ready_checks_database(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "READY"}


def test_root_describes_service(client):
    body = client.get("/").json()
    assert body["service"] == "CareSlot API"
    assert body["docs"] == "/docs"


def test_metrics_exposes_prometheus_format(client):
    client.get("/api/doctors")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "careslot_appointments_booked_total" in response.text
