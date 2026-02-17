from django.contrib import admin
from apps.warranty.models import Warranty
from datetime import date


@admin.register(Warranty)
class WarrantyAdmin(admin.ModelAdmin):

    # ================= LIST VIEW =================
    list_display = (
        "customer_name",
        "car_make_model",
        "vin_chassis_number",
        "ppf_category",
        "approval_status",
        "warranty_code",
        "warranty_end_date",
        "created_at",
    )

    # ================= FILTERS =================
    list_filter = (
        "approval_status",
        "ppf_category",
        "installation_date",
        "created_at",
    )

    # ================= SEARCH =================
    search_fields = (
        "customer_name",
        "email",
        "phone_number",
        "car_make_model",
        "vin_chassis_number",
        "warranty_code",
    )

    # ================= READONLY FIELDS =================
    readonly_fields = (
        "warranty_code",
        "warranty_start_date",
        "warranty_end_date",
        "approved_by",
        "approved_at",
        "created_at",
    )

    # ================= ORGANIZED FIELDSETS =================
    fieldsets = (

        ("Customer Information", {
            "fields": (
                "customer_name",
                "email",
                "phone_number",
                "city",
                "state",
            )
        }),

        ("Vehicle & Installation", {
            "fields": (
                "car_make_model",
                "vin_chassis_number",
                "installation_date",
                "ppf_category",
                "installer_studio_name",
            )
        }),

        ("Uploads", {
            "fields": (
                "installation_proof",
                "car_front_view",
                "car_back_view",
                "car_left_view",
                "car_right_view",
                "car_roof_view",
            )
        }),

        ("Approval Section", {
            "fields": (
                "approval_status",
                "approved_by",
                "approved_at",
            )
        }),

        ("Warranty Details", {
            "fields": (
                "warranty_code",
                "warranty_start_date",
                "warranty_end_date",
            )
        }),

        ("System Info", {
            "fields": ("created_at",)
        }),
    )

    ordering = ("-created_at",)
    actions = ["approve_selected"]

    def approve_selected(self, request, queryset):
        for warranty in queryset:
            if warranty.approval_status != "APPROVED":
                warranty.approval_status = "APPROVED"
                warranty.approved_by = request.user
                warranty.approved_at = date.today()
                warranty.start_warranty()
                warranty.save()

    approve_selected.short_description = "Approve selected warranties"
