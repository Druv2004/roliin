from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils.timezone import now
from django.db.models import Count
from drf_spectacular.utils import extend_schema, extend_schema_view
from apps.warranty.models import Warranty, ContactEnquiry
from django.core.mail import send_mail
from django.conf import settings
from apps.warranty.serializers import (
    WarrantyCreateSerializer,
    WarrantyReadSerializer,
    
    ContactCreateSerializer,
    ContactReadSerializer
)
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from django.template import TemplateDoesNotExist


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
)
class WarrantyViewSet(viewsets.ModelViewSet):

    queryset = Warranty.objects.all().order_by("-created_at")
    parser_classes = [MultiPartParser, FormParser]

    # ================= PERMISSIONS =================
    def get_permissions(self):
        if self.action in [
            "approve",
            "reject",
            "list",
            "destroy",
            "update",
            "partial_update",
        ]:
            return [IsAdminUser()]
        if self.action in ["create", "check"]:
            return [AllowAny()]
        return [IsAdminUser()]

    # ================= SERIALIZER SWITCH =================
    def get_serializer_class(self):
        if self.action == "create":
            return WarrantyCreateSerializer
        return WarrantyReadSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context





    def get_queryset(self):
        qs = Warranty.objects.all().order_by("-created_at")
        status_param = self.request.query_params.get("status")  # NOT_APPROVED / APPROVED / REJECTED
        if status_param in ["NOT_APPROVED", "APPROVED", "REJECTED"]:
            qs = qs.filter(approval_status=status_param)
        return qs



    # ================= CREATE WARRANTY =================
    @extend_schema(
        tags=["Warranty"],
        summary="Register E-Warranty",
        request={"multipart/form-data": WarrantyCreateSerializer},
        responses=WarrantyReadSerializer,
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        warranty = serializer.save()

        return Response(
            {
                "message": "Warranty registered successfully. Awaiting approval.",
                "data": WarrantyReadSerializer(warranty).data,
            },
            status=status.HTTP_201_CREATED,
        )

    # ================= APPROVE WARRANTY =================
    @extend_schema(
        tags=["Warranty (Admin)"],
        summary="Approve warranty",
        responses=WarrantyReadSerializer,
    )
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        warranty = self.get_object()

        if warranty.approval_status == "APPROVED":
            return Response({"message": "Warranty already approved"}, status=status.HTTP_400_BAD_REQUEST)

        warranty.approval_status = "APPROVED"
        warranty.approved_by = request.user
        warranty.approved_at = now().date()

        warranty.start_warranty()
        warranty.save()

        subject = "Roliin Warranty Activated"

        context = {
            "customer_name": warranty.customer_name,
            "warranty_code": warranty.warranty_code,
            "car_make_model": warranty.car_make_model,
            "ppf_variant": warranty.get_ppf_variant_display(),
            "start_date": warranty.warranty_start_date,
            "end_date": warranty.warranty_end_date,
            "support_email": settings.DEFAULT_FROM_EMAIL,
            "brand_name": "Roliin",
        }

        html_content = render_to_string("email/warranty_activated.html", context)
        text_content = strip_tags(html_content)  # fallback

        email_sent = False
        email_error = None

        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[warranty.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)
            email_sent = True
        except Exception as e:
            email_error = str(e)

        return Response(
            {
                "message": "Warranty approved.",
                "email_sent": email_sent,
                "email_error": email_error,
                "data": WarrantyReadSerializer(warranty).data,
            },
            status=status.HTTP_200_OK,
        )

    # ================= REJECT WARRANTY =================
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
                status=status.HTTP_400_BAD_REQUEST,
            )

        warranty.approval_status = "REJECTED"
        warranty.approved_by = request.user
        warranty.approved_at = now().date()
        warranty.save()

        subject = "Roliin Warranty Request Update"

        context = {
            "customer_name": warranty.customer_name,
            "car_make_model": warranty.car_make_model,
            "ppf_variant": warranty.get_ppf_variant_display(),
            "brand_name": "Roliin",
            "support_email": settings.DEFAULT_FROM_EMAIL,
            "rejection_reason": request.data.get("reason", None),
        }

        email_sent = False
        email_error = None

        try:
            html_content = render_to_string("email/warranty_rejected.html", context)
            text_content = strip_tags(html_content)

            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[warranty.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)

            email_sent = True

        except TemplateDoesNotExist:
            email_error = "Template not found: emails/warranty_rejected.html"
        except Exception as e:
            email_error = str(e)

        return Response(
            {
                "message": "Warranty rejected successfully.",
                "email_sent": email_sent,
                "email_error": email_error,
            },
            status=status.HTTP_200_OK,
        )

    # ================= CHECK WARRANTY (PUBLIC) =================
    @extend_schema(
        tags=["Warranty"],
        summary="Check warranty by code",
        parameters=[
            OpenApiParameter(
                name="warranty_code",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Warranty code (example: WR-2026-03-0004-C3E4)",
            )
        ],
        responses=WarrantyReadSerializer,
    )
    @action(detail=False, methods=["get"], url_path="check")
    def check(self, request):
        warranty_code = request.query_params.get("warranty_code")

        if not warranty_code:
            return Response(
                {"error": "Warranty code is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            warranty = Warranty.objects.get(
                warranty_code=warranty_code,
                approval_status="APPROVED",
            )
        except Warranty.DoesNotExist:
            return Response(
                {"message": "Invalid warranty code or not approved"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(WarrantyReadSerializer(warranty, context={"request": request}).data)
    
    @action(detail=False, methods=["get"], permission_classes=[IsAdminUser])
    def stats(self, request):
        """
        Returns warranty counts by approval_status for dashboard cards.
        """
        qs = Warranty.objects.all()
        grouped = qs.values("approval_status").annotate(count=Count("id"))

        counts = {
            "pending": 0,   # NOT_APPROVED
            "approved": 0,  # APPROVED
            "rejected": 0,  # REJECTED
            "total": qs.count(),
        }

        for row in grouped:
            status = row["approval_status"]
            c = row["count"]

            if status == "NOT_APPROVED":
                counts["pending"] = c
            elif status == "APPROVED":
                counts["approved"] = c
            elif status == "REJECTED":
                counts["rejected"] = c

        return Response(counts, status=200)









@extend_schema_view(
    list=extend_schema(
        tags=["Contact (Admin)"],
        summary="List all enquiries (Admin only)",
        responses=ContactReadSerializer(many=True),
    ),
    retrieve=extend_schema(
        tags=["Contact (Admin)"],
        summary="Retrieve enquiry by ID",
        responses=ContactReadSerializer,
    ),
)
class ContactViewSet(viewsets.ModelViewSet):

    queryset = ContactEnquiry.objects.all().order_by("-created_at")
    parser_classes = [MultiPartParser, FormParser]

    # ================= PERMISSIONS =================
    def get_permissions(self):
        if self.action in ["create"]:
            return [AllowAny()]
        return [IsAdminUser()]

    # ================= SERIALIZER SWITCH =================
    def get_serializer_class(self):
        if self.action == "create":
            return ContactCreateSerializer
        return ContactReadSerializer

    # ================= CREATE API =================
    @extend_schema(
        tags=["Contact"],
        summary="Send Contact Enquiry",
        request={"multipart/form-data": ContactCreateSerializer},
        responses=ContactReadSerializer,
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enquiry = serializer.save()

        return Response(
            {
                "message": "Enquiry submitted successfully. We will contact you soon.",
                "data": ContactReadSerializer(enquiry).data
            },
            status=status.HTTP_201_CREATED
        )