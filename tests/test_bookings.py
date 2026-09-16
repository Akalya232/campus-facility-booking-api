from datetime import date, time

import pytest
from httpx import ASGITransport, AsyncClient

from auth import create_access_token, hash_password
from main import app
from models import User, Facility, Booking
from services.notification_service import NotificationServiceError


async def create_test_user(db, name, email):
    user = User(
        name=name,
        email=email,
        password_hash=hash_password("Test@123")
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


async def create_test_facility(db):
    facility = Facility(
        name="Test Seminar Hall",
        location="Test Building",
        capacity=50
    )

    db.add(facility)
    await db.commit()
    await db.refresh(facility)

    return facility


@pytest.mark.asyncio
async def test_create_booking_success(
    test_db,
    override_get_db
):
    user = await create_test_user(
        test_db,
        "Test User",
        "user1@example.com"
    )

    facility = await create_test_facility(test_db)

    token = create_access_token(user.id)

    booking_data = {
        "user_id": user.id,
        "facility_id": facility.id,
        "date": "2026-09-20",
        "start_time": "10:00:00",
        "end_time": "11:00:00",
        "purpose": "Project meeting"
    }

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:

        response = await client.post(
            "/bookings",
            json=booking_data,
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

    assert response.status_code == 201

    data = response.json()

    assert data["user_id"] == user.id
    assert data["facility_id"] == facility.id
    assert data["purpose"] == "Project meeting"


@pytest.mark.asyncio
async def test_create_booking_invalid_time(
    test_db,
    override_get_db
):
    user = await create_test_user(
        test_db,
        "Test User",
        "user2@example.com"
    )

    facility = await create_test_facility(test_db)

    token = create_access_token(user.id)

    booking_data = {
        "user_id": user.id,
        "facility_id": facility.id,
        "date": "2026-09-20",
        "start_time": "12:00:00",
        "end_time": "11:00:00",
        "purpose": "Invalid booking"
    }

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:

        response = await client.post(
            "/bookings",
            json=booking_data,
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

    assert response.status_code == 400
    assert "Start time must be before end time" in response.json()["detail"]


@pytest.mark.asyncio
async def test_booking_conflict(
    test_db,
    override_get_db
):
    user1 = await create_test_user(
        test_db,
        "User One",
        "user3@example.com"
    )

    user2 = await create_test_user(
        test_db,
        "User Two",
        "user4@example.com"
    )

    facility = await create_test_facility(test_db)

    token1 = create_access_token(user1.id)
    token2 = create_access_token(user2.id)

    first_booking = {
        "user_id": user1.id,
        "facility_id": facility.id,
        "date": "2026-09-20",
        "start_time": "10:00:00",
        "end_time": "12:00:00",
        "purpose": "First booking"
    }

    second_booking = {
        "user_id": user2.id,
        "facility_id": facility.id,
        "date": "2026-09-20",
        "start_time": "11:00:00",
        "end_time": "13:00:00",
        "purpose": "Conflicting booking"
    }

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:

        response1 = await client.post(
            "/bookings",
            json=first_booking,
            headers={
                "Authorization": f"Bearer {token1}"
            }
        )

        response2 = await client.post(
            "/bookings",
            json=second_booking,
            headers={
                "Authorization": f"Bearer {token2}"
            }
        )

    assert response1.status_code == 201
    assert response2.status_code == 409


@pytest.mark.asyncio
async def test_booking_authorization_boundary(
    test_db,
    override_get_db
):
    user1 = await create_test_user(
        test_db,
        "Owner",
        "owner@example.com"
    )

    user2 = await create_test_user(
        test_db,
        "Other User",
        "other@example.com"
    )

    facility = await create_test_facility(test_db)

    booking = Booking(
        user_id=user1.id,
        facility_id=facility.id,
        date=date(2026, 9, 20),
        start_time=time(10, 0),
        end_time=time(11, 0),
        purpose="Private booking"
    )

    test_db.add(booking)
    await test_db.commit()
    await test_db.refresh(booking)

    token2 = create_access_token(user2.id)

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:

        response = await client.get(
            f"/bookings/{booking.id}",
            headers={
                "Authorization": f"Bearer {token2}"
            }
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_booking_created_when_notification_fails(
    test_db,
    override_get_db,
    monkeypatch
):
    user = await create_test_user(
        test_db,
        "Notification Test User",
        "notification@example.com"
    )

    facility = await create_test_facility(test_db)

    token = create_access_token(user.id)

    async def failing_notification(
        user_email,
        message
    ):
        raise NotificationServiceError(
            "Notification service failed"
        )

    monkeypatch.setattr(
        "main.send_booking_notification",
        failing_notification
    )

    booking_data = {
        "user_id": user.id,
        "facility_id": facility.id,
        "date": "2026-09-21",
        "start_time": "14:00:00",
        "end_time": "15:00:00",
        "purpose": "Notification failure test"
    }

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:

        response = await client.post(
            "/bookings",
            json=booking_data,
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

    assert response.status_code == 201
    assert response.json()["purpose"] == "Notification failure test"