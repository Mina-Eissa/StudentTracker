from .grade import GradeViewSet
from .teacher_grade import TeacherGradeViewSet
from .student import StudentViewSet
from .student_grade import StudentGradeViewSet
from .session import SessionViewSet
from .attendance import AttendanceViewSet
from .bathroom_log import BathroomLogViewSet
from .behavior import BehaviorViewSet
from .session_student_behavior import SessionStudentBehaviorViewSet
from .event_log import EventLogViewSet
from .subject import SubjectViewSet
from .academic_year import AcademicYearViewSet

__all__ = [
    "AcademicYearViewSet",
    "GradeViewSet",
    "TeacherGradeViewSet",
    "StudentViewSet",
    "StudentGradeViewSet",
    "SessionViewSet",
    "AttendanceViewSet",
    "BathroomLogViewSet",
    "BehaviorViewSet",
    "SessionStudentBehaviorViewSet",
    "EventLogViewSet",
    "SubjectViewSet",
]
