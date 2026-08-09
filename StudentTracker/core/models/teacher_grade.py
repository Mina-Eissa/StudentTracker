import uuid

from django.db import models


class TeacherGrade(models.Model):
    """Many-to-many: which teachers are assigned to which grades."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    teacher = models.ForeignKey(
        "core.AppUser", on_delete=models.CASCADE, db_column="teacher_id", related_name="teacher_grades"
    )
    grade = models.ForeignKey(
        "core.Grade", on_delete=models.CASCADE, db_column="grade_id", related_name="teacher_grades"
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "teacher_grade"
        managed = False
        unique_together = (("teacher", "grade"),)
