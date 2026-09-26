from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers

from ..models import Session, AppUser


class SessionSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(read_only=True)
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=AppUser.objects.all(), required=False)
    academic_year_label = serializers.CharField(
        source="academic_year.label", read_only=True)

    class Meta:
        model = Session
        fields = ["id", "title", "status", "start_at", "duration",
                  "created_at", "creator", "teacher", "grade", "subject", "academic_year_label"]
        read_only_fields = ["status", "creator", "academic_year_label"]

    def validate_start_at(self, value):
        if self.instance is None and value < timezone.now() - timedelta(minutes=1):
            raise serializers.ValidationError(
                "start_at cannot be in the past.")
        return value
