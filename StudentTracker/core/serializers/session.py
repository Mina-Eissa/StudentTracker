from rest_framework import serializers

from ..models import Session


class SessionSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Session
        fields = ["id", "title", "start_at", "duration", "created_at", "creator", "teacher", "grade"]
        read_only_fields = ["creator"]
