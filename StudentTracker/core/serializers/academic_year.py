from rest_framework import serializers
from core.models import AcademicYear


class AcademicYearSerializer(serializers.ModelSerializer):

    class Meta:
        model = AcademicYear
        fields = ["id", "label", "current", "start_date", "end_date"]
