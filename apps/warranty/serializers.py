
from rest_framework import serializers
from apps.warranty.models import Warranty


class WarrantyCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Warranty
        exclude = (
            "approval_status",
            "approved_by",
            "approved_at",
            "warranty_code",
            "warranty_start_date",
            "warranty_end_date",
            "created_at",
        )

    def validate_vin_chassis_number(self, value):
        if len(value) != 17:
            raise serializers.ValidationError("VIN must be exactly 17 characters.")
        return value


class WarrantyReadSerializer(serializers.ModelSerializer):
    approved_by = serializers.StringRelatedField()

    class Meta:
        model = Warranty
        fields = "__all__"


class WarrantyAdminActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warranty
        fields = (
            "approval_status",
            "approved_at",
            "warranty_code",
            "warranty_start_date",
            "warranty_end_date",
        )
        read_only_fields = fields
