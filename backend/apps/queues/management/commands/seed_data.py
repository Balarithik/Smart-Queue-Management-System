from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import User
from apps.analytics.models import AnalyticsRecord
from apps.organizations.models import AgentCounter, Organization
from apps.queues.models import QueueEntry, Service, Ticket


class Command(BaseCommand):
    help = "Seed demo data for smart queue"

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(
            username="orgadmin",
            defaults={"role": "org_admin", "phone_number": "15550000001", "email": "org@example.com"},
        )
        admin.set_password("Password123!")
        admin.save()

        user, _ = User.objects.get_or_create(
            username="demo_user",
            defaults={"role": "user", "phone_number": "15550000002", "email": "user@example.com"},
        )
        user.set_password("Password123!")
        user.save()

        org, _ = Organization.objects.get_or_create(name="City Hospital", slug="city-hospital", defaults={"admin": admin})
        service1, _ = Service.objects.get_or_create(organization=org, code="consult", defaults={"name": "Consultation"})
        Service.objects.get_or_create(organization=org, code="lab", defaults={"name": "Lab Test"})
        counter, _ = AgentCounter.objects.get_or_create(organization=org, name="Counter A", defaults={"agent": admin})

        entry, _ = QueueEntry.objects.get_or_create(
            service=service1, user=user, defaults={"position": 1, "estimated_wait_minutes": 5, "status": "waiting"}
        )
        Ticket.objects.get_or_create(queue_entry=entry, defaults={"token": "CONSULT-0001", "counter": counter})

        AnalyticsRecord.objects.get_or_create(
            service=service1,
            period_start=timezone.now() - timedelta(hours=1),
            period_end=timezone.now(),
            defaults={"avg_wait_minutes": 7.5, "throughput": 18, "abandonment_rate": 0.08},
        )
        self.stdout.write(self.style.SUCCESS("Seed data loaded"))
