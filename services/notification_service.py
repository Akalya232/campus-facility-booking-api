import asyncio


class NotificationServiceError(Exception):
    pass


async def send_booking_notification(
    user_email: str,
    message: str
):
    try:
        # Simulate an external notification service
        await asyncio.wait_for(
            asyncio.sleep(0.1),
            timeout=2.0
        )

        print(
            f"Notification sent to {user_email}: {message}"
        )

        return {
            "status": "sent",
            "recipient": user_email
        }

    except asyncio.TimeoutError:
        raise NotificationServiceError(
            "Notification service timed out"
        )

    except Exception:
        raise NotificationServiceError(
            "Notification service failed"
        )