
# 🏥 Patient Encounter Management System (MEMS)

A **FastAPI-based backend application** to manage **patients, doctors, and medical appointments** in a clinic setting.

This system supports creating and retrieving patients and doctors, and scheduling medical appointments while enforcing **real-world validation rules** such as timezone-safe scheduling and conflict prevention.

---

## 📌 Features

* Create and retrieve patients
* Create and retrieve doctors
* Schedule medical appointments
* Prevent overlapping appointments per doctor
* Enforce future-only appointment booking
* Validate active doctor status
* Filter appointments by date and doctor
* Timezone-aware datetime handling (UTC)
* Unit and integration tests with pytest
* Code coverage reporting (≥80%)
* Linting, formatting, and security scanning
* CI-ready for GitHub Actions

---

## 🏗 Tech Stack

* **FastAPI** – API framework
* **SQLAlchemy 2.0** – ORM
* **Pydantic v2** – Data validation
* **Alembic** – Database migrations
* **SQLite** – Local/testing database
* **MySQL / PostgreSQL** – Production-ready
* **Pytest** – Testing framework
* **Ruff** – Linting
* **Black** – Code formatting
* **Bandit** – Security scanning

---

## 📂 Project Structure

```
patient-encounter-system/
│
├── src/
│   ├── main.py
│   ├── database.py
│   ├── models/
│   │   └── models.py
│   ├── schemas/
│   │   ├── patient.py
│   │   ├── doctor.py
│   │   └── appointment.py
│   └── services/
│       ├── patient_service.py
│       ├── doctor_service.py
│       ├── appointment_service.py
│       └── utils.py
│
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_services.py
│   └── test_routes.py
│
├── alembic/
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## 🚀 Setup Instructions

### 1️⃣ Clone the repository

```bash
git clone <https://github.com/Narasimha2005/patient-encounter-system>
cd patient-encounter-system
```

---

### 2️⃣ Create and activate virtual environment

```bash
python -m venv venv
```

**Windows**

```powershell
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

---

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🗄 Database Initialization

* **SQLite** is used by default for local development and testing
* **MySQL** is recommended for production
* Database schema is managed using **Alembic**

### Run migrations

```bash
alembic upgrade head
```

You can configure the database URL in:

```python
src/database.py
```

---

## ▶️ Running the Application

From the project root:

```bash
uvicorn src.main:app --reload
```

Application runs at:

```
http://127.0.0.1:8000
```

Interactive API documentation:

```
http://127.0.0.1:8000/docs
```

---

## 🧪 Running Tests

Run all tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=src --cov-fail-under=80
```

---

## 🧹 Linting

```bash
ruff check src tests
```

Auto-fix issues:

```bash
ruff check src tests --fix
```

---

## 🎨 Formatting

Check formatting:

```bash
black --check .
```

Format code:

```bash
black .
```

---

## 🔒 Security Scan

```bash
bandit -r src
```

---

## 📌 Appointment Rules

* Appointments must be scheduled **in the future**
* Doctors must be **active**
* No overlapping appointments for the same doctor
* Back-to-back appointments are allowed
* Appointment duration must be **15–180 minutes**
* All times are handled in **UTC**
* Appointment end time is **derived, never stored**

---

## 📬 API Endpoints

### Patients

* `POST /patients` – Create a patient
* `GET /patients/{id}` – Retrieve a patient

### Doctors

* `POST /doctors` – Create a doctor
* `GET /doctors/{id}` – Retrieve a doctor

### Appointments

* `POST /appointments` – Schedule an appointment
* `GET /appointments?date=YYYY-MM-DD&doctor_id=ID` – List appointments

---

## ✅ CI Ready

The project is ready for GitHub Actions CI pipelines and includes:

* `pytest`
* `pytest-cov`
* `ruff`
* `black`
* `bandit`
* Alembic migrations

CI fails if:

* Tests fail
* Coverage < 80%
* Linting or security checks fail

---

## 👤 Author

**Chitturi Narasimhacharyulu**
