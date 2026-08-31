from django.dispatch import receiver
from django.utils import timezone

from .models import EventLog, BathroomLog
from .signals import session_set, session_started, session_ended, grade_assigned


def _log(event_type, triggered_by, **entity_kwargs):
    EventLog.objects.create(event_type=event_type, triggered_by=triggered_by, **entity_kwargs)


@receiver(session_set)
def log_session_set(sender, session, triggered_by, **kwargs):
    _log("session_set", triggered_by, session=session)


@receiver(session_started)
def log_session_started(sender, session, triggered_by, **kwargs):
    _log("session_started", triggered_by, session=session, metadata={"previous_status": "Pending"})


@receiver(session_ended)
def log_session_ended(sender, session, triggered_by, **kwargs):
    _log("session_ended", triggered_by, session=session, metadata={"previous_status": "Running"})


@receiver(grade_assigned)
def log_grade_assigned(sender, teacher_grade, triggered_by, **kwargs):
    _log("grade_assigned", triggered_by, teacher_grade=teacher_grade)


# --- the actual point of doing this: reactions that don't live in the sender ---

@receiver(session_ended)
def close_open_bathroom_trips(sender, session, triggered_by, **kwargs):
    """EndSessionView no longer imports BathroomLog at all — it just
    announces the session ended, and this reacts independently."""
    now = timezone.now()
    open_logs = BathroomLog.objects.filter(session=session, duration__isnull=True)
    for log in open_logs:
        log.duration = round((now - log.started_at).total_seconds() / 60, 2)
        log.save(update_fields=["duration"])
