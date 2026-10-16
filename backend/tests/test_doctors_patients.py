def test_create_and_list_doctors(client, doctor):
    assert doctor["id"] > 0
    listed = client.get("/api/doctors").json()
    assert [d["full_name"] for d in listed] == ["Dr. Test House"]


def test_update_doctor(client, doctor):
    response = client.put(f"/api/doctors/{doctor['id']}", json={"room": "99", "active": False})
    assert response.status_code == 200
    assert response.json()["room"] == "99"
    assert client.get("/api/doctors", params={"active_only": True}).json() == []


def test_delete_doctor_then_404(client, doctor):
    assert client.delete(f"/api/doctors/{doctor['id']}").status_code == 204
    assert client.get(f"/api/doctors/{doctor['id']}").status_code == 404


def test_doctor_validation_error(client):
    response = client.post("/api/doctors", json={"full_name": "X", "specialty": ""})
    assert response.status_code == 422


def test_patient_crud_and_search(client, patient):
    client.post("/api/patients", json={"full_name": "Bob Builder", "email": "bob@example.com"})
    assert len(client.get("/api/patients").json()) == 2
    found = client.get("/api/patients", params={"q": "jane"}).json()
    assert [p["email"] for p in found] == ["jane@example.com"]

    updated = client.put(f"/api/patients/{patient['id']}", json={"phone": "+91 99999"}).json()
    assert updated["phone"] == "+91 99999"
    assert client.delete(f"/api/patients/{patient['id']}").status_code == 204


def test_duplicate_patient_email_conflict(client, patient):
    response = client.post("/api/patients", json={"full_name": "Jane Again", "email": "jane@example.com"})
    assert response.status_code == 409


def test_invalid_patient_email_rejected(client):
    response = client.post("/api/patients", json={"full_name": "No Mail", "email": "not-an-email"})
    assert response.status_code == 422
