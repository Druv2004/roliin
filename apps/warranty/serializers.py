
from rest_framework import serializers
from apps.warranty.models import Warranty



# class WarrantySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Warranty
#         fields = '__all__'
#         read_only_fields = (
#             'approval_status',
#             'warranty_start_date',
#             'warranty_end_date',
#             'created_at',
#             'updated_at',
#         )

class WarrantyCreateSerializer(serializers.ModelSerializer):
    car_image_with_ppf = serializers.ImageField()
    rc_photo = serializers.ImageField()

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