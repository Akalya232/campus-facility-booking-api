# Campus Facility Booking API

A backend API for managing campus users, facilities, and facility bookings.

Built with **FastAPI**, **SQLAlchemy**, **PostgreSQL**, **Alembic**, and **JWT authentication**.

## Features

* User registration and login
* JWT-based authentication
* User profile management
* Facility management
* Facility booking management
* Booking time validation
* Booking conflict detection
* Resource ownership authorization
* Booking search and filtering
* Pagination
* Notification service integration
* Structured logging and error handling
* Database transaction rollback
* Automated API tests
* Interactive OpenAPI/Swagger documentation

---

## Technology Stack

| Technology         | Purpose                      |
| ------------------ | ---------------------------- |
| Python             | Backend programming language |
| FastAPI            | REST API framework           |
| SQLAlchemy         | Database ORM                 |
| PostgreSQL         | Production database          |
| Alembic            | Database migrations          |
| Pydantic           | Request/response validation  |
| JWT                | Authentication               |
| Argon2             | Password hashing             |
| pytest             | Automated testing            |
| SQLite + aiosqlite | Isolated test database       |

---

# 1. Project Setup

## Prerequisites

Install:

* Python 3.12+
* PostgreSQL
* Git

Clone the repository:

```bash
git clone https://github.com/Akalya232/campus-facility-booking-api.git
cd campus-facility-booking-api
```

Create a virtual environment:

### Windows PowerShell

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

# 2. Environment Variables

Create a `.env` file in the project root:

```text
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/campus_booking
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
```

## Required variables

| Variable         | Description                           |
| ---------------- | ------------------------------------- |
| `DATABASE_URL`   | PostgreSQL connection URL             |
| `JWT_SECRET_KEY` | Secret used to sign JWT access tokens |
| `JWT_ALGORITHM`  | JWT signing algorithm                 |

### Important

Do not commit `.env` to Git.

Use a strong random value for `JWT_SECRET_KEY` in real deployments.

---

# 3. Database Setup

Create the PostgreSQL database:

```sql
CREATE DATABASE campus_booking;
```

The application uses PostgreSQL through SQLAlchemy's asynchronous driver.

The main tables are:

* `users`
* `facilities`
* `bookings`
* `alembic_version`

---

# 4. Database Migrations

Apply all existing migrations:

```powershell
alembic upgrade head
```

To create a new migration after changing the database models:

```powershell
alembic revision --autogenerate -m "describe the change"
```

Then apply it:

```powershell
alembic upgrade head
```

To check the current migration version:

```powershell
alembic current
```

To view migration history:

```powershell
alembic history
```

---

# 5. Run the API

Start the development server:

```powershell
uvicorn main:app --reload
```
## Production Deployment

For production, do not use `--reload`.

Start the API with:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000

The API will be available at:

```text
http://127.0.0.1:8000
```

---

# 6. API Documentation

Interactive Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

ReDoc documentation:

```text
http://127.0.0.1:8000/redoc
```

OpenAPI schema:

```text
http://127.0.0.1:8000/openapi.json
```

---

# 7. Health Check

### Request

```http
GET /health
```

### Example response

```json
{
  "status": "ok",
  "database": "connected"
}
```

---

# 8. Authentication

## Register a user

### Request

```http
POST /users
Content-Type: application/json
```

### Example body

```json
{
  "name": "Test User",
  "email": "test@example.com",
  "password": "Test@123"
}
```

### Expected response

```json
{
  "id": 1,
  "name": "Test User",
  "email": "test@example.com"
}
```

---

## Login

### Request

```http
POST /login
Content-Type: application/json
```

### Example body

```json
{
  "email": "test@example.com",
  "password": "Test@123"
}
```

### Example response

```json
{
  "access_token": "YOUR_JWT_TOKEN",
  "token_type": "bearer"
}
```

Use the returned token for protected endpoints:

```text
Authorization: Bearer YOUR_JWT_TOKEN
```

---

# 9. User Endpoints

| Method | Endpoint           | Purpose                      |
| ------ | ------------------ | ---------------------------- |
| POST   | `/users`           | Register a user              |
| GET    | `/users`           | List users                   |
| GET    | `/users/{user_id}` | Get a user                   |
| PATCH  | `/users/{user_id}` | Update a user                |
| DELETE | `/users/{user_id}` | Delete a user                |
| GET    | `/users/me`        | Get logged-in user's profile |

Protected user endpoints require a valid JWT token.

---

# 10. Facility Endpoints

| Method | Endpoint                    | Purpose           |
| ------ | --------------------------- | ----------------- |
| POST   | `/facilities`               | Create a facility |
| GET    | `/facilities`               | List facilities   |
| GET    | `/facilities/{facility_id}` | Get a facility    |
| PATCH  | `/facilities/{facility_id}` | Update a facility |
| DELETE | `/facilities/{facility_id}` | Delete a facility |

### Example: Create a facility

```http
POST /facilities
Content-Type: application/json
```

```json
{
  "name": "Seminar Hall",
  "location": "Main Block",
  "capacity": 100
}
```

---

# 11. Booking Endpoints

| Method | Endpoint                 | Purpose              |
| ------ | ------------------------ | -------------------- |
| POST   | `/bookings`              | Create a booking     |
| GET    | `/bookings`              | List user's bookings |
| GET    | `/bookings/{booking_id}` | Get a booking        |
| PATCH  | `/bookings/{booking_id}` | Update a booking     |
| DELETE | `/bookings/{booking_id}` | Delete a booking     |

Booking endpoints require authentication.

---

## Create a Booking

### Request

```http
POST /bookings
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

### Example body

```json
{
  "user_id": 1,
  "facility_id": 1,
  "date": "2026-09-20",
  "start_time": "10:00:00",
  "end_time": "11:00:00",
  "purpose": "Project meeting"
}
```

The API uses the authenticated user's ID as the booking owner.

---

## Search and Filter Bookings

The booking list endpoint supports:

* Date filtering
* Facility filtering
* Purpose search
* Pagination

### Example

```http
GET /bookings?date=2026-09-20&facility_id=1&purpose=meeting&skip=0&limit=10
Authorization: Bearer YOUR_JWT_TOKEN
```

---

# 12. Booking Validation

The API rejects invalid booking times.

For example:

```json
{
  "start_time": "12:00:00",
  "end_time": "11:00:00"
}
```

returns:

```json
{
  "detail": "Start time must be before end time"
}
```

If another booking already occupies the requested time:

```json
{
  "detail": "Facility is already booked for this time"
}
```

The API returns HTTP `409 Conflict`.

---

# 13. Authorization

Booking resources are protected by ownership checks.

A logged-in user can access their own bookings, while attempts to access another user's booking are rejected.

Protected requests require:

```text
Authorization: Bearer YOUR_JWT_TOKEN
```

---

# 14. Notification Service

The project contains a separate notification service layer:

```text
services/
└── notification_service.py
```

The booking workflow calls the notification service after a successful booking.

Notification failures are handled separately so that a notification problem does not undo an already committed booking.

---

# 15. Automated Tests

Run all tests with:

```powershell
pytest
```

The test suite covers:

* Successful booking creation
* Invalid booking time
* Booking conflicts
* Authorization boundaries
* Notification service failure
* Notification service success

The API tests use an isolated in-memory SQLite database, so test data does not affect the development PostgreSQL database.

---

# 16. Project Structure

```text
campus-facility-booking-api/
│
├── main.py
├── database.py
├── models.py
├── schemas.py
├── auth.py
├── requirements.txt
├── .env
│
├── services/
│   ├── __init__.py
│   └── notification_service.py
│
├── tests/
│   ├── conftest.py
│   ├── test_bookings.py
│   └── test_notification_service.py
│
└── alembic/
    ├── versions/
    └── ...
```

---

# 17. Common Commands

### Start server

```powershell
uvicorn main:app --reload
```

### Run tests

```powershell
pytest
```

### Check Python syntax

```powershell
python -m py_compile main.py
```

### Apply migrations

```powershell
alembic upgrade head
```

### Check migration version

```powershell
alembic current
```

---

## API Base URL

For local development:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```
## Final Review Demo Sequence

Use the following sequence to demonstrate the working backend:

1. Start PostgreSQL and apply migrations:
   ```bash
   alembic upgrade head