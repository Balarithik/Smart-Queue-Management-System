from channels.layers import get_channel_layer
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from apps.organizations.models import AgentCounter
from .models import QueueEntry, Service, Ticket
from .serializers import QRJoinSerializer, QueueEntrySerializer, ServiceSerializer, TicketSerializer
from .services import join_queue, publish_queue_event


class IsOrgOrAgent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["org_admin", "agent"]


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.select_related("organization")
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]


class QueueViewSet(viewsets.GenericViewSet):
    queryset = QueueEntry.objects.select_related("service", "user", "ticket")
    serializer_class = QueueEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["post"])
    def join(self, request):
        service = Service.objects.get(pk=request.data["service"])
        entry = join_queue(service, request.user)
        return Response(QueueEntrySerializer(entry).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def join_qr(self, request):
        serializer = QRJoinSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = Service.objects.select_related("organization").get(
            organization__slug=serializer.validated_data["organization_slug"], code=serializer.validated_data["service_code"]
        )
        entry = join_queue(service, request.user)
        return Response(QueueEntrySerializer(entry).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        entry = self.get_object()
        entry.status = QueueEntry.Status.CANCELLED
        entry.save(update_fields=["status", "updated_at"])
        return Response({"status": "cancelled"})

    @action(detail=False, methods=["post"], permission_classes=[IsOrgOrAgent])
    def call_next(self, request):
        service = Service.objects.get(pk=request.data["service"])
        counter = AgentCounter.objects.get(pk=request.data["counter"])
        entry = QueueEntry.objects.filter(service=service, status=QueueEntry.Status.WAITING).order_by("created_at").first()
        if not entry:
            return Response({"detail": "No waiting entries"}, status=404)
        entry.status = QueueEntry.Status.CALLED
        entry.save(update_fields=["status", "updated_at"])
        ticket = entry.ticket
        ticket.counter = counter
        ticket.called_at = timezone.now()
        ticket.save(update_fields=["counter", "called_at"])
        publish_queue_event(get_channel_layer(), f"service_{service.id}", "ticket.called", TicketSerializer(ticket).data)
        return Response(TicketSerializer(ticket).data)

    @action(detail=False, methods=["post"], permission_classes=[IsOrgOrAgent])
    def serve_next(self, request):
        ticket = Ticket.objects.select_related("queue_entry").get(pk=request.data["ticket"])
        ticket.queue_entry.status = QueueEntry.Status.DONE
        ticket.queue_entry.save(update_fields=["status", "updated_at"])
        ticket.served_at = timezone.now()
        ticket.save(update_fields=["served_at"])
        return Response(TicketSerializer(ticket).data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def ticket_pdf(request, ticket_id):
    return HttpResponse(f"Ticket printable stub for {ticket_id}", content_type="text/plain")
