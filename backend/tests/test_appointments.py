def book(client, doctor, patient, when, duration=30):
    return client.post(
        "/api/appointments",
        json={
            "patient_id": patient["id"],
            "doctor_id": doctor["id"],
            "scheduled_at": when,
            "duration_minutes": duration,
            "reason": "Consultation",
        },
    )


def test_book_appointment(client, appointment, doctor, patient):
    assert appointment["status"] == "SCHEDULED"
    assert appointment["doctor_name"] == doctor["full_name"]
    assert appointment["patient_name"] == patient["full_name"]
    assert appointment["specialty"] == "Cardiology"


def test_get_and_list_appointments(client, appointment):
    assert client.get(f"/api/appointments/{appointment['id']}").json()["id"] == appointment["id"]
    assert len(client.get("/api/appointments").json()) == 1
    assert len(client.get("/api/appointments", params={"on_date": "2030-01-15"}).json()) == 1
    assert client.get("/api/appointments", params={"on_date": "2030-01-16"}).json() == []
    assert client.get("/api/appointments", params={"status_filter": "COMPLETED"}).json() == []


def test_double_booking_is_rejected(client, appointment, doctor, patient):
    overlapping = book(client, doctor, patient, "2030-01-15T10:15:00Z")
    assert overlapping.status_code == 409
    back_to_back = book(client, doctor, patient, "2030-01-15T10:30:00Z")
    assert back_to_back.status_code == 201


def test_cancelled_slot_can_be_rebooked(client, appointment, doctor, patient):
    client.put(f"/api/appointments/{appointment['id']}", json={"status": "CANCELLED"})
    assert book(client, doctor, patient, "2030-01-15T10:00:00Z").status_code == 201


def test_status_workflow(client, appointment):
    url = f"/api/appointments/{appointment['id']}"
    assert client.put(url, json={"status": "CHECKED_IN"}).json()["status"] == "CHECKED_IN"
    assert client.put(url, json={"status": "COMPLETED"}).json()["status"] == "COMPLETED"
    # Completed is terminal.
    assert client.put(url, json={"status": "SCHEDULED"}).status_code == 409


def test_reschedule_checks_conflicts(client, appointment, doctor, patient):
    other = book(client, doctor, patient, "2030-01-15T12:00:00Z").json()
    clash = client.put(f"/api/appointments/{other['id']}", json={"scheduled_at": "2030-01-15T10:10:00Z"})
    assert clash.status_code == 409
    moved = client.put(f"/api/appointments/{other['id']}", json={"scheduled_at": "2030-01-15T14:00:00Z"})
    assert moved.status_code == 200
    assert moved.json()["scheduled_at"].startswith("2030-01-15T14:00:00")


def test_booking_requires_existing_patient_and_active_doctor(client, doctor, patient):
    missing = client.post(
        "/api/appointments",
        json={"patient_id": 999, "doctor_id": doctor["id"], "scheduled_at": "2030-01-01T09:00:00Z", "reason": "x y"},
    )
    assert missing.status_code == 404
    client.put(f"/api/doctors/{doctor['id']}", json={"active": False})
    assert book(client, doctor, patient, "2030-01-01T09:00:00Z").status_code == 409


def test_delete_appointment(client, appointment):
    assert client.delete(f"/api/appointments/{appointment['id']}").status_code == 204
    assert client.get(f"/api/appointments/{appointment['id']}").status_code == 404


def test_stats(client, appointment, doctor, patient):
    book(client, doctor, patient, "2030-01-15T11:00:00Z")
    client.put(f"/api/appointments/{appointment['id']}", json={"status": "CANCELLED"})
    stats = client.get("/api/appointments/stats").json()
    assert stats["total"] == 2
    assert stats["scheduled"] == 1
    assert stats["cancelled"] == 1
    assert stats["patients"] == 1
    assert stats["active_doctors"] == 1
    assert stats["doctor_load"][0]["upcoming"] == 1


def test_seed_demo_data_populates_empty_db(client):
    from app.seed import seed_demo_data
    from tests.conftest import TestSession

    with TestSession() as db:
        assert seed_demo_data(db) is True
        assert seed_demo_data(db) is False  # idempotent
    assert len(client.get("/api/doctors").json()) == 5
    assert client.get("/api/appointments/stats").json()["total"] == 8
