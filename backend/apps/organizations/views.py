from rest_framework import permissions, viewsets
from .models import AgentCounter, Organization
from .serializers import AgentCounterSerializer, OrganizationSerializer


class IsOrgAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "org_admin"


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsOrgAdmin]


class AgentCounterViewSet(viewsets.ModelViewSet):
    queryset = AgentCounter.objects.select_related("organization", "agent")
    serializer_class = AgentCounterSerializer
    permission_classes = [IsOrgAdmin]
