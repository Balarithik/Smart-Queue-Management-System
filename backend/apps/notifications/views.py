from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView


class NotificationSettingsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "phone_number": request.user.phone_number,
                "whatsapp_opt_in": request.user.whatsapp_opt_in,
            }
        )

    def patch(self, request):
        request.user.whatsapp_opt_in = bool(request.data.get("whatsapp_opt_in", request.user.whatsapp_opt_in))
        request.user.save(update_fields=["whatsapp_opt_in"])
        return self.get(request)
