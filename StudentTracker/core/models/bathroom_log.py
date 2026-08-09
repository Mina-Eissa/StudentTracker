import uuid

from django.db import models


class BathroomLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    count_times = models.IntegerField(default=0)
    duration_each_time = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text="minutes")
    session = models.ForeignKey(
        "core.Session", on_delete=models.CASCADE, db_column="session_id", related_name="bathroom_logs"
    )
    student = models.ForeignKey(
        "core.Student", on_delete=models.CASCADE, db_column="student_id", related_name="bathroom_logs"
    )

    class Meta:
        db_table = "bathroom_log"
        managed = False
        unique_together = (("session", "student"),)
