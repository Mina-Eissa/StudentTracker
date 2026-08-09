from rest_framework import serializers

from ..models import SessionStudentBehavior


class SessionStudentBehaviorSerializer(serializers.ModelSerializer):
    # exposes the DB's misspelled "conseqence" column as "consequence" to the frontend
    consequence = serializers.CharField(source="conseqence", required=False, allow_blank=True)

    class Meta:
        model = SessionStudentBehavior
        fields = ["id", "comment", "consequence", "session", "student", "behavior"]
