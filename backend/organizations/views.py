from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsOrganizationRole
from organizations.models import Organization
from organizations.permissions import IsOrganizationOwnerOrAdmin
from organizations.serializers import (
    OrganizationCreateSerializer,
    OrganizationSerializer,
    QueueSerializer,
)
from queues.models import Queue


class OrganizationCreateView(generics.CreateAPIView):
    """POST /api/organizations/ — create org for the current user (ORGANIZATION or ADMIN role)."""

    permission_classes = [IsAuthenticated, IsOrganizationRole]
    serializer_class = OrganizationCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        org = serializer.save()
        return Response(
            OrganizationSerializer(org).data,
            status=status.HTTP_201_CREATED,
        )


class OrganizationMeView(generics.RetrieveAPIView):
    """GET /api/organizations/me/ — current user's organization."""

    permission_classes = [IsAuthenticated, IsOrganizationRole]
    serializer_class = OrganizationSerializer

    def get_object(self):
        return get_object_or_404(Organization, owner=self.request.user)


class OrganizationQueuesView(APIView):
    """GET /api/organizations/<pk>/queues/"""

    permission_classes = [IsAuthenticated, IsOrganizationOwnerOrAdmin]

    def get(self, request, pk):
        org = get_object_or_404(Organization, pk=pk)
        self.check_object_permissions(request, org)
        qs = Queue.objects.filter(organization=org)
        data = QueueSerializer(qs, many=True).data
        return Response(data)


class OrganizationStatsView(APIView):
    """GET /api/organizations/<pk>/stats/"""

    permission_classes = [IsAuthenticated, IsOrganizationOwnerOrAdmin]

    def get(self, request, pk):
        org = get_object_or_404(Organization, pk=pk)
        self.check_object_permissions(request, org)
        qs = org.queues.all()
        return Response(
            {
                "organization_id": org.id,
                "name": org.name,
                "queue_count": qs.count(),
                "active_queue_count": qs.filter(is_active=True).count(),
            }
        )
