from rest_framework import serializers


class DailySeriesPointSerializer(serializers.Serializer):
    date = serializers.DateField()
    joins = serializers.IntegerField()
    called = serializers.IntegerField(required=False, default=0)
    completed = serializers.IntegerField()


class QueueSummarySerializer(serializers.Serializer):
    queue_id = serializers.IntegerField()
    public_id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.SlugField()
    is_active = serializers.BooleanField()
    joins = serializers.IntegerField()
    completed = serializers.IntegerField()


class OrganizationReportSerializer(serializers.Serializer):
    organization_id = serializers.IntegerField()
    name = serializers.CharField()
    days = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    queue_count = serializers.IntegerField()
    active_queue_count = serializers.IntegerField()
    total_entries = serializers.IntegerField()
    waiting_count = serializers.IntegerField()
    called_count = serializers.IntegerField()
    completed_count = serializers.IntegerField()
    daily_series = DailySeriesPointSerializer(many=True)
    queues = QueueSummarySerializer(many=True)


class QueueReportSerializer(serializers.Serializer):
    queue_id = serializers.IntegerField()
    public_id = serializers.UUIDField()
    name = serializers.CharField()
    organization_id = serializers.IntegerField()
    days = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    total_entries = serializers.IntegerField()
    waiting_count = serializers.IntegerField()
    called_count = serializers.IntegerField()
    completed_count = serializers.IntegerField()
    throughput_per_day = serializers.FloatField()
    avg_wait_seconds = serializers.FloatField()
    daily_series = DailySeriesPointSerializer(many=True)


class SignupDaySerializer(serializers.Serializer):
    date = serializers.DateField(allow_null=True)
    count = serializers.IntegerField()


class UserReportSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    by_role = serializers.DictField(child=serializers.IntegerField())
    signups_by_day = SignupDaySerializer(many=True)
