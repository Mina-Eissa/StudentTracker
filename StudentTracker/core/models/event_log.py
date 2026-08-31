import uuid

from django.db import models

EVENT_TYPE_CHOICES = [
    ("session_set", "session_set"),
    ("session_started", "session_started"),
    ("session_ended", "session_ended"),
    ("grade_assigned", "grade_assigned"),
]


class EventLog(models.Model):
    """Append-only. Written exclusively by signal receivers (see receivers.py)
    as a side effect of an action — never created or edited directly through
    the API."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    session = models.ForeignKey(
        "core.Session", on_delete=models.CASCADE, db_column="session_id",
        null=True, blank=True, related_name="events",
    )
    teacher_grade = models.ForeignKey(
        "core.TeacherGrade", on_delete=models.CASCADE, db_column="teacher_grade_id",
        null=True, blank=True, related_name="events",
    )
    triggered_by = models.ForeignKey(
        "core.AppUser", on_delete=models.PROTECT, db_column="triggered_by", related_name="triggered_events"
    )
    metadata = models.JSONField(null=True, blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "event_log"
        managed = False
        ordering = ["-occurred_at"]
