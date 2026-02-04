from datetime import datetime, timedelta, timezone


def test_create_and_get_patient(client):
    res = client.post(
        "/patients",
        json={
            "first_name": "Ramesh",
            "last_name": "Kumar",
            "email_address": "ramesh@test.com",
            "phone_number": "9999999999",
        },
    )
    assert res.status_code == 201
    patient_id = res.json()["id"]

    res = client.get(f"/patients/{patient_id}")
    assert res.status_code == 200
    assert res.json()["email_address"] == "ramesh@test.com"


def test_get_patient_not_found(client):
    res = client.get("/patients/999")
    assert res.status_code == 404


def test_create_and_get_doctor(client):
    res = client.post(
        "/doctors",
        json={
            "full_name": "Dr. Rao",
            "medical_specialization": "Cardiology",
            "active_status": True,
        },
    )
    assert res.status_code == 201
    doctor_id = res.json()["id"]

    res = client.get(f"/doctors/{doctor_id}")
    assert res.status_code == 200


def test_create_appointment(client):
    patient = client.post(
        "/patients",
        json={
            "first_name": "A",
            "last_name": "B",
            "email_address": "a@test.com",
            "phone_number": "123",
        },
    ).json()

    doctor = client.post(
        "/doctors",
        json={
            "full_name": "Dr. Test",
            "medical_specialization": "General",
            "active_status": True,
        },
    ).json()

    start_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

    res = client.post(
        "/appointments",
        json={
            "patient_id": patient["id"],
            "doctor_id": doctor["id"],
            "appointment_start_datetime": start_time,
            "appointment_duration": 30,
        },
    )

    assert res.status_code == 201
    assert res.json()["appointment_duration"] == 30


def test_overlapping_appointments_conflict(client):
    patient = client.post(
        "/patients",
        json={
            "first_name": "X",
            "last_name": "Y",
            "email_address": "xy@test.com",
            "phone_number": "111",
        },
    ).json()

    doctor = client.post(
        "/doctors",
        json={
            "full_name": "Dr Conflict",
            "medical_specialization": "General",
            "active_status": True,
        },
    ).json()

    start_time = datetime.now(timezone.utc) + timedelta(hours=2)

    res1 = client.post(
        "/appointments",
        json={
            "patient_id": patient["id"],
            "doctor_id": doctor["id"],
            "appointment_start_datetime": start_time.isoformat(),
            "appointment_duration": 60,
        },
    )
    assert res1.status_code == 201

    res2 = client.post(
        "/appointments",
        json={
            "patient_id": patient["id"],
            "doctor_id": doctor["id"],
            "appointment_start_datetime": (
                start_time + timedelta(minutes=30)
            ).isoformat(),
            "appointment_duration": 30,
        },
    )

    assert res2.status_code == 409


def test_list_appointments(client):
    res = client.get("/appointments?date=2099-01-01")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
