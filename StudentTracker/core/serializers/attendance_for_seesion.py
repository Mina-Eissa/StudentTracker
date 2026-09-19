from rest_framework import serializers
from core.models.attendance import Attendance


class AttendanceForSessionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(
        source='student_grade.student.full_name', read_only=True)

    class Meta:
        model = Attendance
        fields = ["id", "status", "reason", "session", "student_name"]
