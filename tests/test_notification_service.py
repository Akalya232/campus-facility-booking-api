import pytest

from services.notification_service import (
    send_booking_notification,
    NotificationServiceError
)


@pytest.mark.asyncio
async def test_notification_service():
    result = await send_booking_notification(
        "test@example.com",
        "Booking confirmed"
    )

    assert result["status"] == "sent"
    assert result["recipient"] == "test@example.com"