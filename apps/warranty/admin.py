from django.contrib import admin
from apps.warranty.models import Warranty


@admin.register(Warranty)
class WarrantyAdmin(admin.ModelAdmin):
    list_display = (
        'customer_name',
        'car_number',
        'ppf_category',
        'approval_status',
        'warranty_end_date',
        'created_at',
    )
    list_filter = ('approval_status', 'ppf_category')
    search_fields = (
        'customer_name',
        'car_number',
        'roliin_roll_unique_code',
    )
