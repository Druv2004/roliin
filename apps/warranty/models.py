# ================================ WARRANTY MODELS ==================================
import uuid
from django.db import models
from datetime import date
from dateutil.relativedelta import relativedelta
from django.conf import settings


class Warranty(models.Model):

    # ===================== PPF CATEGORY =====================
    PPF_CATEGORY_CHOICES = [
        ('GLOSS_6', 'Gloss PPF – 6 Years'),
        ('GLOSS_10', 'Gloss PPF – 10 Years'),
        ('MATTE_6', 'Matte PPF – 6 Years'),
        ('BLACK_6', 'Black PPF – 6 Years'),
    ]

    WARRANTY_YEARS_MAP = {
        'GLOSS_6': 6,
        'GLOSS_10': 10,
        'MATTE_6': 6,
        'BLACK_6': 6,
    }

    APPROVAL_STATUS_CHOICES = [
        ('NOT_APPROVED', 'Not Approved'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    # ===================== CUSTOMER INFORMATION =====================
    # 🔐 UUID Primary Key
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    customer_name = models.CharField(max_length=100, default="")
    email = models.EmailField(default="")
    phone_number = models.CharField(max_length=15, default="")
    city = models.CharField(max_length=100, default="")
    state = models.CharField(max_length=100, default="")

    # ===================== VEHICLE INFORMATION =====================
    car_make_model = models.CharField(max_length=150, default="")  # Merged field
    vin_chassis_number = models.CharField(max_length=50, default="")
    installation_date = models.DateField(null=True, blank=True)

    # ===================== PPF DETAILS =====================
    ppf_category = models.CharField(max_length=20, choices=PPF_CATEGORY_CHOICES, default="")
    installer_studio_name = models.CharField(max_length=150, default="")

    # ===================== UPLOADS =====================

    # Invoice / Proof
    installation_proof = models.FileField(upload_to='warranty/proof/', default="")

    # Car View Images
    car_front_view = models.ImageField(upload_to='warranty/car_views/', default="")
    car_back_view = models.ImageField(upload_to='warranty/car_views/', default="")
    car_left_view = models.ImageField(upload_to='warranty/car_views/', default="")
    car_right_view = models.ImageField(upload_to='warranty/car_views/', default="")
    car_roof_view = models.ImageField(upload_to='warranty/car_views/',default="")

    # ===================== APPROVAL SYSTEM =====================
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='NOT_APPROVED'
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    approved_at = models.DateField(null=True, blank=True)

    # ===================== WARRANTY DATES =====================
    warranty_start_date = models.DateField(null=True, blank=True)
    warranty_end_date = models.DateField(null=True, blank=True)

    warranty_code = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )

    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # ===================== WARRANTY HELPERS =====================

    def generate_warranty_code(self):
        today = date.today()
        year = today.year
        month = f"{today.month:02d}"

        count = Warranty.objects.filter(
            approval_status='APPROVED',
            approved_at__year=year,
            approved_at__month=today.month
        ).count() + 1

        random_code = uuid.uuid4().hex[:4].upper()

        return f"WR-{year}-{month}-{count:04d}-{random_code}"

    def start_warranty(self):
        years = self.WARRANTY_YEARS_MAP.get(self.ppf_category, 0)
        self.warranty_start_date = date.today()
        self.warranty_end_date = date.today() + relativedelta(years=years)
        self.warranty_code = self.generate_warranty_code()

    def __str__(self):
        return f"{self.customer_name} - {self.car_make_model}"
