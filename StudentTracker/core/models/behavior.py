import uuid

from django.db import models

BEHAVIOR_TYPE_CHOICES = [("Positive", "Positive"), ("Negative", "Negative")]


class Behavior(models.Model):
    """Catalog of behavior types/tags (e.g. 'Talking out of turn', 'Helped a classmate')."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    type = models.CharField(max_length=10, choices=BEHAVIOR_TYPE_CHOICES)
    tag = models.CharField(max_length=100)
    point = models.IntegerField(default=0)

    class Meta:
        db_table = "behavior"
        managed = False

    def __str__(self):
        return self.tag
