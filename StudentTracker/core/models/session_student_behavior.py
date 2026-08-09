import uuid

from django.db import models


class SessionStudentBehavior(models.Model):
    """Event log: which student showed which behavior in which session."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    comment = models.TextField(null=True, blank=True)
    # NOTE: column is spelled "conseqence" (typo) in the DB — kept as-is to match exactly
    conseqence = models.TextField(null=True, blank=True, db_column="conseqence")
    session = models.ForeignKey(
        "core.Session", on_delete=models.CASCADE, db_column="session_id", related_name="behavior_events"
    )
    student = models.ForeignKey(
        "core.Student", on_delete=models.CASCADE, db_column="student_id", related_name="behavior_events"
    )
    behavior = models.ForeignKey(
        "core.Behavior", on_delete=models.PROTECT, db_column="behavior_id", related_name="events"
    )

    class Meta:
        db_table = "session_student_behavior"
        managed = False

    @property
    def consequence(self):
        """Friendly accessor for the misspelled DB column."""
        return self.conseqence
