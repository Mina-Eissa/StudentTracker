import uuid

from django.db import models


class Subject(models.Model):
    """Catalog of subjects (e.g. Math, Science) — a session references one,
    separate from its free-text title."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "subject"
        managed = False

    def __str__(self):
        return self.name
