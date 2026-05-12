from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.permissions import IsAdminRole, IsOrganizationRole
from accounts.serializers import (
    RegisterSerializer,
    RoleTokenObtainPairSerializer,
    UserSerializer,
)
from accounts.tokens import issue_tokens

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = issue_tokens(user)
        body = UserSerializer(user).data | tokens
        return Response(body, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = RoleTokenObtainPairSerializer


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class AdminPingView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        return Response({"detail": "admin", "user": request.user.username})


class OrganizationPingView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationRole]

    def get(self, request):
        return Response({"detail": "organization", "user": request.user.username})
