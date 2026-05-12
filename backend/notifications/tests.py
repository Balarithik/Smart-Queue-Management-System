from unittest.mock import MagicMock, patch

from django.test import TransactionTestCase, SimpleTestCase

from accounts.models import User
from notifications.hooks import (
    notify_queue_closed,
    notify_user_became_active,
    notify_user_joined_queue,
)
from notifications.services import NotificationEvent, reset_notification_orchestrator_for_tests
from organizations.models import Organization
from queues.models import Queue, QueueEntry
from queues.services import join_queue


class NotificationHookUnitTests(SimpleTestCase):
    def tearDown(self) -> None:
        reset_notification_orchestrator_for_tests()

    @patch("notifications.hooks.get_notification_orchestrator")
    def test_notify_user_joined_queue_dispatches(self, get_orch):
        orch = MagicMock()
        get_orch.return_value = orch
        queue = MagicMock()
        queue.public_id = "550e8400-e29b-41d4-a716-446655440000"
        queue.name = "Desk"
        queue.organization_id = 3
        entry = MagicMock()
        entry.pk = 9
        entry.token = 42

        notify_user_joined_queue(queue, entry, waiting_ahead=2)

        orch.dispatch.assert_called_once()
        ctx = orch.dispatch.call_args[0][0]
        self.assertEqual(ctx.event, NotificationEvent.USER_JOINED_QUEUE)
        self.assertEqual(ctx.token, 42)
        self.assertEqual(ctx.metadata.get("waiting_ahead"), 2)

    @patch("notifications.hooks.get_notification_orchestrator")
    def test_notify_user_became_active_dispatches(self, get_orch):
        orch = MagicMock()
        get_orch.return_value = orch
        queue = MagicMock()
        queue.public_id = "550e8400-e29b-41d4-a716-446655440000"
        queue.name = "Desk"
        queue.organization_id = 1
        entry = MagicMock()
        entry.pk = 2
        entry.token = 5
        entry.status = QueueEntry.Status.CALLED

        notify_user_became_active(queue, entry)

        orch.dispatch.assert_called_once()
        ctx = orch.dispatch.call_args[0][0]
        self.assertEqual(ctx.event, NotificationEvent.USER_BECAME_ACTIVE)

    @patch("notifications.hooks.get_notification_orchestrator")
    def test_notify_queue_closed_dispatches(self, get_orch):
        orch = MagicMock()
        get_orch.return_value = orch
        queue = MagicMock()
        queue.public_id = "550e8400-e29b-41d4-a716-446655440000"
        queue.name = "Desk"
        queue.organization_id = 7

        notify_queue_closed(queue, reason="manual")

        orch.dispatch.assert_called_once()
        ctx = orch.dispatch.call_args[0][0]
        self.assertEqual(ctx.event, NotificationEvent.QUEUE_CLOSED)
        self.assertEqual(ctx.metadata.get("reason"), "manual")


class JoinQueueNotificationTransactionTests(TransactionTestCase):
    """``transaction.on_commit`` for join runs when the outer test is not wrapped in atomic."""

    def setUp(self):
        reset_notification_orchestrator_for_tests()
        self.owner = User.objects.create_user(
            username="n_owner",
            password="securepass1",
            role=User.Role.ORGANIZATION,
        )
        self.org = Organization.objects.create(
            owner=self.owner,
            name="Clinic",
            slug="clinic-n",
        )
        self.queue = Queue.objects.create(
            organization=self.org,
            name="Desk",
            slug="desk-n",
        )

    def tearDown(self) -> None:
        reset_notification_orchestrator_for_tests()

    @patch("notifications.hooks.notify_user_joined_queue")
    def test_join_queue_schedules_notification_on_commit(self, notify_join):
        join_queue(self.queue.public_id)
        notify_join.assert_called_once()
        args, kwargs = notify_join.call_args
        self.assertEqual(args[0].pk, self.queue.pk)
        self.assertEqual(kwargs.get("waiting_ahead"), 0)


class QueueCloseSignalTransactionTests(TransactionTestCase):
    def setUp(self):
        reset_notification_orchestrator_for_tests()
        self.owner = User.objects.create_user(
            username="c_owner",
            password="securepass1",
            role=User.Role.ORGANIZATION,
        )
        self.org = Organization.objects.create(
            owner=self.owner,
            name="Clinic C",
            slug="clinic-c",
        )
        self.queue = Queue.objects.create(
            organization=self.org,
            name="Desk C",
            slug="desk-c",
        )

    def tearDown(self) -> None:
        reset_notification_orchestrator_for_tests()

    @patch("notifications.signals.notify_queue_closed")
    def test_deactivating_queue_calls_close_hook(self, notify_closed):
        self.queue.is_active = False
        self.queue.save(update_fields=["is_active"])
        notify_closed.assert_called_once()
