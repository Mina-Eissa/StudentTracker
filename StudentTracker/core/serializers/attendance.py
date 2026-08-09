from rest_framework import serializers

from ..models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ["id", "status", "reason", "session", "student"]
