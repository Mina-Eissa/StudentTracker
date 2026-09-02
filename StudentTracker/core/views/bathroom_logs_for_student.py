from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from core.models import Student, BathroomLog


class BathroomLogsForStudentView(APIView):
    """
    API view to retrieve bathroom logs for a specific student.
    by passing the student_id in the URL.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        student = get_object_or_404(Student, id=student_id)
        try:
            logs = BathroomLog.objects.filter(student=student)
            logs_data = [
                {
                    "student_id": str(student.id),
                    "student_name": student.name,
                    "id": str(log.id),
                    "started_at": log.started_at,
                    "duration": float(log.duration),
                    "session_id": str(log.session.id),
                    "set_by": str(log.set_by.id),
                }
                for log in logs
            ]
            return Response(logs_data, status=status.HTTP_200_OK)
        except BathroomLog.DoesNotExist:
            return Response({"error": "No bathroom logs found for the specified student."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
