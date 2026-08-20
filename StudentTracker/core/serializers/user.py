from rest_framework import serializers

from ..models import AppUser


class AppUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppUser
        fields = ["id", "first_name", "middle_name",
                  "last_name", "email", "role", "created_at"]
        # accounts are created by the Supabase Auth trigger, not through this API
        read_only_fields = fields
