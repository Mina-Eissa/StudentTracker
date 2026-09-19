import uuid

from django.db import models


class SessionStatus(models.TextChoices):
    PENDING = "Pending", "Pending"
    RUNNING = "Running", "Running"
    FINISHED = "Finished", "Finished"


class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=256)
    start_at = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=SessionStatus.choices,
        default=SessionStatus.PENDING,
    )
    duration = models.IntegerField(help_text="minutes")
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(
        "core.AppUser", on_delete=models.PROTECT, db_column="creator_id", related_name="created_sessions"
    )
    teacher = models.ForeignKey(
        "core.AppUser", on_delete=models.PROTECT, db_column="teacher_id", related_name="taught_sessions"
    )
    grade = models.ForeignKey(
        "core.Grade", on_delete=models.PROTECT, db_column="grade_id", related_name="sessions"
    )
    academic_year = models.ForeignKey(
        "core.AcademicYear", on_delete=models.PROTECT, db_column="academic_year_id", related_name="sessions"
    )
    subject = models.ForeignKey(
        "core.Subject", on_delete=models.PROTECT, db_column="subject_id",
        null=True, blank=True, related_name="sessions",
    )

    class Meta:
        db_table = "session"
        managed = False

    def __str__(self):
        return self.title
