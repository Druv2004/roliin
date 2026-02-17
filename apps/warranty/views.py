from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema, extend_schema_view
from apps.warranty.models import Warranty
from apps.warranty.serializers import (
    WarrantyCreateSerializer,
    WarrantyReadSerializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=["Warranty (Admin)"],
        summary="List all warranties (Admin only)",
        responses=WarrantyReadSerializer(many=True),
    ),
    retrieve=extend_schema(
        tags=["Warranty (Admin)"],
        summary="Retrieve warranty by ID",
        responses=WarrantyReadSerializer,
    ),
    destroy=extend_schema(
        tags=["Warranty (Admin)"],
        summary="Delete warranty (Admin only)",
    ),
)
class WarrantyViewSet(viewsets.ModelViewSet):

    queryset = Warranty.objects.all().order_by("-created_at")
    parser_classes = [MultiPartParser, FormParser]

    # 🔐 Permissions
    def get_permissions(self):
        if self.action in ["approve", "reject", "list", "destroy", "update", "partial_update"]:
            return [IsAdminUser()]
        if self.action in ["create", "check"]:
            return [AllowAny()]
        return [IsAdminUser()]

    # 🔁 Serializer Switching
    def get_serializer_class(self):
        if self.action == "create":
            return WarrantyCreateSerializer
        return WarrantyReadSerializer

    # ✅ Create Warranty (🔥 FIXED FOR FILE UPLOAD IN SWAGGER)
    @extend_schema(
        tags=["Warranty"],
        summary="Register E-Warranty",
        description="Public endpoint to register new E-Warranty.",
        request={
            "multipart/form-data": WarrantyCreateSerializer
        },
        responses=WarrantyReadSerializer,
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        warranty = serializer.save()

        return Response(
            {
                "message": "Warranty registered successfully. Awaiting approval.",
                "data": WarrantyReadSerializer(warranty).data
            },
            status=status.HTTP_201_CREATED
        )

    # ✅ Approve Warranty
    @extend_schema(
        tags=["Warranty (Admin)"],
        summary="Approve warranty",
        description="Approve warranty and generate warranty code (Admin only)",
        responses=WarrantyReadSerializer,
    )
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        warranty = self.get_object()

        if warranty.approval_status == "APPROVED":
            return Response(
                {"message": "Warranty already approved"},
                status=status.HTTP_400_BAD_REQUEST
            )

        warranty.approval_status = "APPROVED"
        warranty.approved_by = request.user
        warranty.approved_at = now().date()
        warranty.start_warranty()
        warranty.save()

        return Response(
            WarrantyReadSerializer(warranty).data,
            status=status.HTTP_200_OK
        )

    # ❌ Reject Warranty
    @extend_schema(
        tags=["Warranty (Admin)"],
        summary="Reject warranty",
    )
    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        warranty = self.get_object()

        if warranty.approval_status == "REJECTED":
            return Response(
                {"message": "Warranty already rejected"},
                status=status.HTTP_400_BAD_REQUEST
            )

        warranty.approval_status = "REJECTED"
        warranty.approved_by = request.user
        warranty.approved_at = now().date()
        warranty.save()

        return Response(
            {"message": "Warranty rejected successfully"},
            status=status.HTTP_200_OK
        )

    # 🔍 Public Warranty Check
    @extend_schema(
        tags=["Warranty"],
        summary="Check warranty by code",
        description="Check approved warranty details using warranty code.",
        responses=WarrantyReadSerializer,
    )
    @action(detail=False, methods=["get"])
    def check(self, request):
        warranty_code = request.query_params.get("warranty_code")

        if not warranty_code:
            return Response(
                {"error": "Warranty code is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            warranty = Warranty.objects.get(
                warranty_code=warranty_code,
                approval_status="APPROVED"
            )
        except Warranty.DoesNotExist:
            return Response(
                {"message": "Invalid warranty code or not approved"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(WarrantyReadSerializer(warranty).data)
