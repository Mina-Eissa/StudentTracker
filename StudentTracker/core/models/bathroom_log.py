import uuid

from django.db import models


class BathroomLog(models.Model):
    """One row per bathroom trip (not an aggregate anymore). duration is
    null while the student is still out — that's the 'is this open?' signal."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    session = models.ForeignKey(
        "core.Session", on_delete=models.CASCADE, db_column="session_id", related_name="bathroom_logs"
    )
    student = models.ForeignKey(
        "core.Student", on_delete=models.CASCADE, db_column="student_id", related_name="bathroom_logs"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    duration = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True, help_text="minutes; null while still out"
    )
    set_by = models.ForeignKey(
        "core.AppUser", on_delete=models.PROTECT, db_column="set_by", related_name="bathroom_logs_set"
    )

    class Meta:
        db_table = "bathroom_log"
        managed = False

    @property
    def is_open(self):
        return self.duration is None
