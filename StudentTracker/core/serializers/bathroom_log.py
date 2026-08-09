from rest_framework import serializers

from ..models import BathroomLog


class BathroomLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = BathroomLog
        fields = ["id", "count_times", "duration_each_time", "session", "student"]
        # count_times/duration_each_time are only ever written by the start/stop endpoints
        read_only_fields = ["count_times", "duration_each_time"]
