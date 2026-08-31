from rest_framework import serializers

from ..models import EventLog


class EventLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventLog
        fields = ["id", "event_type", "session", "teacher_grade", "triggered_by", "metadata", "occurred_at"]
        # written only by receivers.py as a side effect — never directly via the API
        read_only_fields = fields
