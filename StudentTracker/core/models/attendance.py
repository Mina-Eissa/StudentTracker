import uuid

from django.db import models

ATTENDANCE_STATUS_CHOICES = [
    ("Present", "Present"),
    ("Absent", "Absent"),
    ("Late", "Late"),
    ("Excused", "Excused"),
    ("Not_Signed", "Not_Signed")
]


class Attendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    status = models.CharField(
        max_length=10, choices=ATTENDANCE_STATUS_CHOICES, default="Not_Signed")
    reason = models.TextField(null=True, blank=True)
    session = models.ForeignKey(
        "core.Session", on_delete=models.CASCADE, db_column="session_id", related_name="attendance_records"
    )
    student_grade = models.ForeignKey(
        "core.StudentGrade", on_delete=models.CASCADE, db_column="student_id", related_name="attendance_records"
    )

    class Meta:
        db_table = "attendance"
        managed = False
        unique_together = (("session", "student_grade"),)
