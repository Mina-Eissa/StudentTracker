import pytest
import uuid
from django.urls import reverse

from core.models import BathroomLog

# Bathroom Start View Tests


@pytest.mark.django_db
def test_start_requires_auth(api_client, session_pending, student):
    response = api_client.post(
        reverse("bathroom-start"),
        {
            "session_id": str(session_pending.id),
            "student_id": str(student.id),
        },
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_start_requires_session_and_student(as_teacher):
    response = as_teacher.post(
        reverse("bathroom-start"),
        {},
        format="json",
    )

    assert response.status_code == 400
    assert response.data["detail"] == (
        "session_id and student_id are required."
    )


@pytest.mark.django_db
def test_start_requires_session_id(as_teacher, student):
    response = as_teacher.post(
        reverse("bathroom-start"),
        {
            "student_id": str(student.id),
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_start_requires_student_id(as_teacher, session_pending):
    response = as_teacher.post(
        reverse("bathroom-start"),
        {
            "session_id": str(session_pending.id),
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_first_call_starts_a_trip(
    as_teacher,
    session_pending,
    student,
    teacher_user,
):
    response = as_teacher.post(
        reverse("bathroom-start"),
        {
            "session_id": str(session_pending.id),
            "student_id": str(student.id),
        },
        format="json",
    )

    assert response.status_code == 201

    assert response.data["action"] == "started"
    assert response.data["is_open"] is True

    bathroom_trip = BathroomLog.objects.get(
        id=response.data["id"]
    )

    assert bathroom_trip.session_id == session_pending.id
    assert bathroom_trip.student_id == student.id
    assert bathroom_trip.set_by_id == teacher_user.id
    assert bathroom_trip.duration is None


@pytest.mark.django_db
def test_second_call_rejected_when_trip_is_open(
    as_teacher,
    session_pending,
    student,
):
    first_response = as_teacher.post(
        reverse("bathroom-start"),
        {
            "session_id": str(session_pending.id),
            "student_id": str(student.id),
        },
        format="json",
    )

    assert first_response.status_code == 201

    second_response = as_teacher.post(
        reverse("bathroom-start"),
        {
            "session_id": str(session_pending.id),
            "student_id": str(student.id),
        },
        format="json",
    )

    assert second_response.status_code == 409


@pytest.mark.django_db
def test_teacher_cannot_start_trip_in_another_teachers_session(
    as_teacher,
    session_of_other_teacher,
    student,
):
    response = as_teacher.post(
        reverse("bathroom-start"),
        {
            "session_id": str(session_of_other_teacher.id),
            "student_id": str(student.id),
        },
        format="json",
    )

    assert response.status_code == 404

    assert not BathroomLog.objects.filter(
        session=session_of_other_teacher,
        student=student,
    ).exists()

# Bathroom Stop View Tests


@pytest.mark.django_db
def test_stop_requires_id(as_teacher):
    response = as_teacher.post(
        reverse("bathroom-stop"),
        {},
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_stop_open_bathroom_trip(
    as_teacher,
    bathroom_log,
):
    assert bathroom_log.is_open is True

    response = as_teacher.post(
        reverse("bathroom-stop"),
        {
            "id": str(bathroom_log.id),
        },
        format="json",
    )

    assert response.status_code == 200

    bathroom_log.refresh_from_db()

    assert bathroom_log.is_open is False
    assert bathroom_log.duration is not None
    assert bathroom_log.duration >= 0


@pytest.mark.django_db
def test_stop_closed_trip_returns_409(
    as_teacher,
    closed_bathroom_log,
):
    response = as_teacher.post(
        reverse("bathroom-stop"),
        {
            "id": str(closed_bathroom_log.id),
        },
        format="json",
    )

    assert response.status_code == 409


@pytest.mark.django_db
def test_stop_nonexistent_trip_returns_404(
    as_teacher,
):
    response = as_teacher.post(
        reverse("bathroom-stop"),
        {
            "id": str(uuid.uuid4()),
        },
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_teacher_cannot_stop_another_teachers_trip(
    as_teacher,
    bathroom_log_of_other_teacher,
):
    response = as_teacher.post(
        reverse("bathroom-stop"),
        {
            "id": str(bathroom_log_of_other_teacher.id),
        },
        format="json",
    )

    assert response.status_code == 404
