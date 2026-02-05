from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.warranty.models import Warranty
from apps.warranty.serializers import WarrantySerializer
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser









@extend_schema_view(
    list=extend_schema(
        tags=["Warranty"],
        summary="List warranties (Restricted)",
        description="Listing warranties is restricted for public users."
    ),
    retrieve=extend_schema(
        tags=["Warranty"],
        summary="Retrieve warranty by ID",
        description="Retrieve a warranty record by its ID (admin use)."
    ),
    create=extend_schema(
        tags=["Warranty"],
        summary="Register E-Warranty",
        description="Register a new E-Warranty for a vehicle. Approval required."
    ),
    update=extend_schema(
        tags=["Warranty"],
        summary="Update warranty",
        description="Update warranty details (admin only)."
    ),
    partial_update=extend_schema(
        tags=["Warranty"],
        summary="Partially update warranty",
        description="Partially update warranty fields (admin only)."
    ),
    destroy=extend_schema(
        tags=["Warranty"],
        summary="Delete warranty",
        description="Delete a warranty record (admin only)."
    ),
)
class WarrantyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Warranty Registration and Status Check
    """

    queryset = Warranty.objects.all().order_by('-created_at')
    serializer_class = WarrantySerializer
    parser_classes = [MultiPartParser, FormParser]

    # 🔒 Optional: restrict list for normal users
    def list(self, request, *args, **kwargs):
        return Response(
            {"message": "Listing warranties is not allowed"},
            status=status.HTTP_403_FORBIDDEN
        )

    # ✅ Warranty Registration (POST)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Warranty registered successfully. Awaiting approval.",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # # 🔍 Warranty Status Check (GET)
    # @extend_schema(
    #     tags=["Warranty"],
    #     summary="Check warranty status",
    #     description="Check warranty status using roliin roll unique code. Only approved warranties are returned.",
    #     parameters=[],
    #     responses={200: WarrantySerializer}
    # )
    # @action(detail=False, methods=['get'], url_path='status')
    # def warranty_status(self, request):
    #     roliin_code = request.query_params.get('roliin_roll_unique_code')

    #     try:
    #         warranty = Warranty.objects.get(
    #             roliin_roll_unique_code=roliin_code,
    #             approval_status='APPROVED'
    #         )
    #     except Warranty.DoesNotExist:
    #         return Response(
    #             {"message": "Warranty not found or not approved"},
    #             status=404
    #         )

    #     return Response(WarrantySerializer(warranty).data)
    
    
    
     # ✅ APPROVE WARRANTY
    @extend_schema(
        tags=["Warranty"],
        summary="Approve warranty",
        description="Approve warranty and start warranty countdown (JWT required)"
    )
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='approve'
    )
    def approve_warranty(self, request, pk=None):
        warranty = self.get_object()

        if warranty.approval_status == 'APPROVED':
            return Response(
                {"message": "Warranty already approved"},
                status=status.HTTP_400_BAD_REQUEST
            )

        warranty.approval_status = 'APPROVED'
        warranty.approved_by = request.user
        warranty.approved_at = date.today()
        warranty.start_warranty()
        warranty.save()

        return Response(
            {
                "message": "Warranty approved successfully",
                "warranty_code": warranty.warranty_code,
                "warranty_start_date": warranty.warranty_start_date,
                "warranty_end_date": warranty.warranty_end_date,
            },
            status=status.HTTP_200_OK
        )

    # ❌ REJECT WARRANTY
    @extend_schema(
        tags=["Warranty"],
        summary="Reject warranty",
        description="Reject warranty (JWT required)"
    )
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='reject'
    )
    def reject_warranty(self, request, pk=None):
        warranty = self.get_object()

        if warranty.approval_status == 'REJECTED':
            return Response(
                {"message": "Warranty already rejected"},
                status=status.HTTP_400_BAD_REQUEST
            )

        warranty.approval_status = 'REJECTED'
        warranty.approved_by = request.user
        warranty.approved_at = date.today()
        warranty.save()

        return Response(
            {"message": "Warranty rejected successfully"},
            status=status.HTTP_200_OK
        )
        
    @extend_schema(
        tags=["Warranty"],
        summary="Check warranty by warranty code",
        description="Check approved warranty details using warranty code"
    )
    @action(detail=False, methods=['get'], url_path='check')
    def check_warranty(self, request):
        warranty_code = request.query_params.get('warranty_code')

        if not warranty_code:
            return Response(
                {"error": "Warranty code is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            warranty = Warranty.objects.get(
                warranty_code=warranty_code,
                approval_status='APPROVED'
            )
        except Warranty.DoesNotExist:
            return Response(
                {"message": "Invalid warranty code or not approved"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            WarrantySerializer(warranty).data,
            status=status.HTTP_200_OK
        )
