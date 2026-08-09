from django.core.cache import cache
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import Session, BathroomLog

BATHROOM_CACHE_PREFIX = "bathroom_open"


def _bathroom_cache_key(session_id, student_id):
    return f"{BATHROOM_CACHE_PREFIX}:{session_id}:{student_id}"


class BathroomStartView(APIView):
    """POST { session_id, student_id } -> marks a student as 'out'.

    NOTE: uses Django's cache framework to hold the open timer between
    start/stop calls. The default LocMemCache is fine for local dev but
    is per-process — for production (multiple workers) point CACHES at
    Redis so start/stop hit the same store.
    """

    def post(self, request):
        session_id = request.data.get("session_id")
        student_id = request.data.get("student_id")
        if not session_id or not student_id:
            return Response({"detail": "session_id and student_id are required."}, status=400)

        session = Session.objects.filter(id=session_id, teacher_id=request.user.id).first()
        if not session:
            return Response({"detail": "Session not found or not yours."}, status=404)

        key = _bathroom_cache_key(session_id, student_id)
        if cache.get(key):
            return Response({"detail": "Student is already out."}, status=409)

        cache.set(key, timezone.now().isoformat(), timeout=60 * 60)  # 1hr safety expiry
        return Response({"status": "started", "started_at": timezone.now()})


class BathroomStopView(APIView):
    """POST { session_id, student_id } -> closes the timer, updates bathroom_log."""

    def post(self, request):
        session_id = request.data.get("session_id")
        student_id = request.data.get("student_id")
        if not session_id or not student_id:
            return Response({"detail": "session_id and student_id are required."}, status=400)

        session = Session.objects.filter(id=session_id, teacher_id=request.user.id).first()
        if not session:
            return Response({"detail": "Session not found or not yours."}, status=404)

        key = _bathroom_cache_key(session_id, student_id)
        started_at_raw = cache.get(key)
        if not started_at_raw:
            return Response({"detail": "No open bathroom timer for this student."}, status=409)

        started_at = timezone.datetime.fromisoformat(started_at_raw)
        duration_minutes = (timezone.now() - started_at).total_seconds() / 60
        cache.delete(key)

        log, created = BathroomLog.objects.get_or_create(
            session_id=session_id,
            student_id=student_id,
            defaults={"count_times": 1, "duration_each_time": round(duration_minutes, 2)},
        )
        if not created:
            new_count = log.count_times + 1
            new_avg = ((log.duration_each_time * log.count_times) + duration_minutes) / new_count
            log.count_times = new_count
            log.duration_each_time = round(new_avg, 2)
            log.save(update_fields=["count_times", "duration_each_time"])

        return Response({
            "status": "stopped",
            "duration_minutes": round(duration_minutes, 2),
            "count_times": log.count_times,
            "duration_each_time": log.duration_each_time,
        })
