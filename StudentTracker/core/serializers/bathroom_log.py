from rest_framework import serializers

from ..models import BathroomLog


class BathroomLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = BathroomLog
        fields = ["id", "started_at", "duration",
                  "session", "student", "set_by"]
        # count_times/duration_each_time are only ever written by the start/stop endpoints
        read_only_fields = ["started_at", "duration"]
