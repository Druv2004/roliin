from rest_framework import serializers
from apps.warranty.models import Warranty, ContactEnquiry


# ========================= CREATE SERIALIZER =========================
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

    # 🔐 VIN Validation
    def validate_vin_chassis_number(self, value):
        if len(value) != 17:
            raise serializers.ValidationError("VIN must be exactly 17 characters.")
        return value.upper()

    # 📅 Installation date validation
    def validate_installation_date(self, value):
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError("Installation date cannot be in the future.")
        return value


# ========================= READ SERIALIZER =========================
class WarrantyReadSerializer(serializers.ModelSerializer):
    approved_by = serializers.StringRelatedField()
    ppf_variant_display = serializers.CharField(
        source="get_ppf_variant_display",
        read_only=True
    )

    class Meta:
        model = Warranty
        fields = "__all__"


# ========================= ADMIN ACTION SERIALIZER =========================
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



# ================= CREATE SERIALIZER =================
class ContactCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactEnquiry
        fields = "__all__"
        read_only_fields = ("id", "created_at")

    def validate_phone_number(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Enter a valid phone number.")
        return value

    def validate(self, attrs):
        if not attrs.get("consent"):
            raise serializers.ValidationError(
                {"consent": "You must agree to be contacted."}
            )
        return attrs


# ================= READ SERIALIZER =================
class ContactReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactEnquiry
        fields = "__all__"
