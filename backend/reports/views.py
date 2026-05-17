from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdminRole
from organizations.models import Organization
from organizations.permissions import IsOrganizationOwnerOrAdmin
from queues.models import Queue
from reports.serializers import (
    OrganizationReportSerializer,
    QueueReportSerializer,
    UserReportSerializer,
)
from reports.services import (
    get_org_report,
    get_queue_report,
    get_user_report,
    parse_days,
)


class OrganizationReportView(APIView):
    """GET /api/reports/organizations/<pk>/ — organization analytics."""

    permission_classes = [IsAuthenticated, IsOrganizationOwnerOrAdmin]

    def get(self, request, pk):
        org = get_object_or_404(Organization, pk=pk)
        self.check_object_permissions(request, org)
        days = parse_days(request.query_params.get("days"))
        data = get_org_report(org, days)
        serializer = OrganizationReportSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class QueueReportView(APIView):
    """GET /api/reports/queues/<public_id>/ — queue analytics."""

    permission_classes = [IsAuthenticated, IsOrganizationOwnerOrAdmin]

    def get(self, request, public_id):
        queue = get_object_or_404(
            Queue.objects.select_related("organization"),
            public_id=public_id,
        )
        self.check_object_permissions(request, queue)
        days = parse_days(request.query_params.get("days"))
        data = get_queue_report(queue, days)
        serializer = QueueReportSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class UserReportView(APIView):
    """GET /api/reports/users/ — platform user analytics (admin only)."""

    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        data = get_user_report()
        serializer = UserReportSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
