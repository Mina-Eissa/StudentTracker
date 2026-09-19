from django.db import models
import uuid


class StudentGrade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        "core.Student", on_delete=models.CASCADE, db_column="student_id", related_name="grade_students")
    grade = models.ForeignKey(
        "core.Grade", on_delete=models.CASCADE, db_column="grade_id", related_name="grade_students")
    academic_year = models.ForeignKey(
        "core.AcademicYear", on_delete=models.CASCADE, db_column="academic_year_id", related_name="grade_students")
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_grade"
        managed = False
        unique_together = (("student", "grade", "academic_year"),)
