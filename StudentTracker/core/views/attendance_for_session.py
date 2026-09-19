from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from core.models import Attendance
from core.serializers.attendance_for_seesion import AttendanceForSessionSerializer


class AttendanceForSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        """
        Retrieve attendance records for a specific session.
        """
        try:
            attendance_records = (Attendance.objects.filter(
                session_id=session_id).select_related('student_grade__student'))
            serializer = AttendanceForSessionSerializer(
                attendance_records, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Attendance.DoesNotExist:
            return Response({"detail": "Attendance records not found."}, status=status.HTTP_404_NOT_FOUND)
