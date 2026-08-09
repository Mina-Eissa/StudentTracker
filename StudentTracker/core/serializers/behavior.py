from rest_framework import serializers

from ..models import Behavior


class BehaviorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Behavior
        fields = ["id", "type", "tag", "point"]
