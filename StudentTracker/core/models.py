import uuid
from django.db import models


# ============================================================
# All models are managed = False: Supabase's SQL Editor is the
# source of truth for the schema. Django just maps onto it.
# ============================================================

ROLE_CHOICES = [("Teacher", "Teacher"), ("Admin", "Admin")]
GRADE_SECTION_CHOICES = [(c, c) for c in "ABCDEF"]
ATTENDANCE_STATUS_CHOICES = [
    ("Present", "Present"),
    ("Absent", "Absent"),
    ("Late", "Late"),
    ("Excused", "Excused"),
]
BEHAVIOR_TYPE_CHOICES = [("Positive", "Positive"), ("Negative", "Negative")]


class AppUser(models.Model):
    """Maps to the "user" table (quoted because it's a reserved word).
    Named AppUser in Django to avoid clashing with django.contrib.auth.User."""

    id = models.UUIDField(primary_key=True)  # == auth.users.id
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=256, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    # Lets DRF's IsAuthenticated permission work without a real auth backend
    is_authenticated = True

    class Meta:
        db_table = "user"
        managed = False

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


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


class TeacherGrade(models.Model):
    """Many-to-many: which teachers are assigned to which grades."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    teacher = models.ForeignKey(
        AppUser, on_delete=models.CASCADE, db_column="teacher_id", related_name="teacher_grades"
    )
    grade = models.ForeignKey(
        Grade, on_delete=models.CASCADE, db_column="grade_id", related_name="teacher_grades"
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "teacher_grade"
        managed = False
        unique_together = (("teacher", "grade"),)


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100)
    school_id = models.CharField(max_length=256, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student"
        managed = False

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.school_id})"


class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=256)
    start_at = models.DateTimeField()
    duration = models.IntegerField(help_text="minutes")
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(
        AppUser, on_delete=models.PROTECT, db_column="creator_id", related_name="created_sessions"
    )
    teacher = models.ForeignKey(
        AppUser, on_delete=models.PROTECT, db_column="teacher_id", related_name="taught_sessions"
    )
    grade = models.ForeignKey(
        Grade, on_delete=models.PROTECT, db_column="grade_id", related_name="sessions"
    )

    class Meta:
        db_table = "session"
        managed = False

    def __str__(self):
        return self.title


class Attendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS_CHOICES)
    reason = models.TextField(null=True, blank=True)
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, db_column="session_id", related_name="attendance_records"
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, db_column="student_id", related_name="attendance_records"
    )

    class Meta:
        db_table = "attendance"
        managed = False
        unique_together = (("session", "student"),)


class BathroomLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    count_times = models.IntegerField(default=0)
    duration_each_time = models.DecimalField(
        max_digits=6, decimal_places=2, default=0, help_text="minutes")
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, db_column="session_id", related_name="bathroom_logs"
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, db_column="student_id", related_name="bathroom_logs"
    )

    class Meta:
        db_table = "bathroom_log"
        managed = False
        unique_together = (("session", "student"),)


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


class SessionStudentBehavior(models.Model):
    """Event log: which student showed which behavior in which session."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    comment = models.TextField(null=True, blank=True)
    # NOTE: column is spelled "conseqence" (typo) in the DB — kept as-is to match exactly
    conseqence = models.TextField(
        null=True, blank=True, db_column="conseqence")
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, db_column="session_id", related_name="behavior_events"
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, db_column="student_id", related_name="behavior_events"
    )
    behavior = models.ForeignKey(
        Behavior, on_delete=models.PROTECT, db_column="behavior_id", related_name="events"
    )

    class Meta:
        db_table = "session_student_behavior"
        managed = False

    @property
    def consequence(self):
        """Friendly accessor for the misspelled DB column."""
        return self.conseqence
