from django.db import models
import uuid

class AcademicYear(models.Model):
    """Catalog of academic years (e.g. '2020-2021', '2021-2022')."""

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    label = models.CharField(max_length=10, unique=True)
    current = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "academic_year"
        managed = False

    def __str__(self):
        return self.label
