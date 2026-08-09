import uuid

from django.db import models

GRADE_SECTION_CHOICES = [(c, c) for c in "ABCDEF"]


class Grade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    level = models.IntegerField()
    section = models.CharField(max_length=1, choices=GRADE_SECTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "grade"
        managed = False

    def __str__(self):
        return f"Grade {self.level}{self.section}"
