"""
Abstract notification layer.

Concrete providers (SendGrid, Twilio, FCM/APNs) can be wired by subclassing
``NotificationChannel`` and registering instances on ``NotificationOrchestrator``.

Environment variables (optional, for future backends) are documented in ``.env.example``.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class NotificationEvent(str, Enum):
    """Domain events that may result in outbound notifications."""

    USER_JOINED_QUEUE = "user_joined_queue"
    USER_BECAME_ACTIVE = "user_became_active"
    QUEUE_CLOSED = "queue_closed"


@dataclass(frozen=True)
class NotificationContext:
    """Immutable payload passed to all channels for one dispatch."""

    event: NotificationEvent
    queue_public_id: str
    queue_name: str
    organization_id: int | None = None
    token: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class NotificationChannel(ABC):
    """Strategy interface for a single delivery medium."""

    name: str = "base"

    @abstractmethod
    def send(self, ctx: NotificationContext) -> None:
        """Deliver or enqueue the notification. Must not raise for placeholder impls."""


class EmailNotificationChannel(NotificationChannel):
    """
    Placeholder email channel.

    Future: SendGrid REST API (``SENDGRID_API_KEY``) or SMTP.
    See: https://docs.sendgrid.com/api-reference/mail-send/mail-send
    """

    name = "email"

    def send(self, ctx: NotificationContext) -> None:
        # Intentionally no I/O: swap for SendGrid client when credentials exist.
        logger.info(
            "[notifications:email] event=%s queue=%s token=%s meta=%s",
            ctx.event.value,
            ctx.queue_public_id,
            ctx.token,
            ctx.metadata,
        )


class SmsNotificationChannel(NotificationChannel):
    """
    Placeholder SMS channel.

    Future: Twilio Messages API (``TWILIO_ACCOUNT_SID``, ``TWILIO_AUTH_TOKEN``, ``TWILIO_FROM_NUMBER``).
    See: https://www.twilio.com/docs/sms
    """

    name = "sms"

    def send(self, ctx: NotificationContext) -> None:
        logger.info(
            "[notifications:sms] event=%s queue=%s token=%s meta=%s",
            ctx.event.value,
            ctx.queue_public_id,
            ctx.token,
            ctx.metadata,
        )


class PushNotificationChannel(NotificationChannel):
    """
    Placeholder mobile/web push channel.

    Future: FCM (Firebase), APNs, or Web Push with device tokens stored per user.
    """

    name = "push"

    def send(self, ctx: NotificationContext) -> None:
        logger.info(
            "[notifications:push] event=%s queue=%s token=%s meta=%s",
            ctx.event.value,
            ctx.queue_public_id,
            ctx.token,
            ctx.metadata,
        )


class NotificationOrchestrator:
    """Fan-out dispatcher across registered channels."""

    def __init__(self, channels: list[NotificationChannel] | None = None) -> None:
        self._channels = channels or [
            EmailNotificationChannel(),
            SmsNotificationChannel(),
            PushNotificationChannel(),
        ]

    def register(self, channel: NotificationChannel) -> None:
        self._channels.append(channel)

    def dispatch(self, ctx: NotificationContext) -> None:
        for channel in self._channels:
            try:
                channel.send(ctx)
            except Exception:
                logger.exception(
                    "Notification channel %s failed for event %s",
                    getattr(channel, "name", type(channel).__name__),
                    ctx.event.value,
                )


_default_orchestrator: NotificationOrchestrator | None = None


def get_notification_orchestrator() -> NotificationOrchestrator:
    global _default_orchestrator
    if _default_orchestrator is None:
        _default_orchestrator = NotificationOrchestrator()
    return _default_orchestrator


def reset_notification_orchestrator_for_tests() -> None:
    """Test helper: clear singleton so tests get a fresh orchestrator."""
    global _default_orchestrator
    _default_orchestrator = None
