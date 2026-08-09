from django.db import models

ROLE_CHOICES = [("Teacher", "Teacher"), ("Admin", "Admin")]


class AppUser(models.Model):
    """Maps to the "user" table (quoted in SQL because it's a reserved word).
    Named AppUser in Django to avoid clashing with django.contrib.auth.User."""

    id = models.UUIDField(primary_key=True)  # == auth.users.id
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=256, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    # lets DRF's IsAuthenticated permission work without a real auth backend
    is_authenticated = True

    class Meta:
        db_table = "user"
        managed = False

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
