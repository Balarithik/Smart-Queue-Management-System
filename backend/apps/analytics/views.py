import csv
from django.http import HttpResponse
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from .models import AnalyticsRecord
from .serializers import AnalyticsRecordSerializer


class AnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AnalyticsRecord.objects.select_related("service")
    serializer_class = AnalyticsRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"])
    def export_csv(self, request):
        rows = self.get_queryset()
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="analytics.csv"'
        writer = csv.writer(response)
        writer.writerow(["service_id", "period_start", "period_end", "avg_wait_minutes", "throughput", "abandonment_rate"])
        for r in rows:
            writer.writerow([r.service_id, r.period_start, r.period_end, r.avg_wait_minutes, r.throughput, r.abandonment_rate])
        return response
