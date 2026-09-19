from rest_framework import serializers

from ..models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    student = serializers.CharField(
        source="student_grade__student__fullname", read_only=True)

    class Meta:
        model = Attendance
        fields = ["id", "status", "reason", "session", "student"]
