from rest_framework import serializers

from ..models import TeacherGrade


class TeacherGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherGrade
        fields = ["id", "teacher", "grade", "assigned_at"]
