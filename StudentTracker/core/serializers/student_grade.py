from rest_framework import serializers
from core.models import StudentGrade


class StudentGradeSerializer(serializers.ModelSerializer):
    grade = serializers.CharField(source="grade.label", read_only=True)
    student_name = serializers.CharField(
        source="student.full_name", read_only=True)
    student_id = serializers.CharField(source="student.id", read_only=True)

    class Meta:
        model = StudentGrade
        fields = ["id", "student_name", "student_id",
                  "grade", "academic_year", "enrolled_at"]
