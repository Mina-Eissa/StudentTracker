from rest_framework import serializers

from ..models import Grade


class GradeSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()

    class Meta:
        model = Grade
        fields = ["id", "label", "level", "section", "created_at"]

    def get_label(self, obj):
        return f"{obj.level}-{obj.section}"
