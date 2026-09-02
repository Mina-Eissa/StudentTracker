from rest_framework import serializers

from ..models import Session, AppUser


class SessionSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(read_only=True)
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=AppUser.objects.all(), required=False)

    class Meta:
        model = Session
        fields = ["id", "title", "status", "start_at", "duration",
                  "created_at", "creator", "teacher", "grade"]
        read_only_fields = ["status", "creator"]
