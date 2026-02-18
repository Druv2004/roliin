# ================================ WARRANTY MODELS ==================================
import uuid
from django.db import models
from datetime import date
from dateutil.relativedelta import relativedelta
from django.conf import settings


class Warranty(models.Model):

    # ===================== PPF VARIANT =====================
    PPF_VARIANT_CHOICES = [
        ('PREMIUM_MATTE_SERIES', 'Premium Matte Series'),
        ('PREMIUM_GLOSS_SERIES', 'Premium Gloss Series'),
        ('TITANIUM_GLOSS_SERIES', 'Titanium Gloss Series'),
        ('PIANO_BLACK_COLOR_PPF_SERIES', 'Piano Black Color PPF Series'),
        ('CHARCOAL_BLACK_COLOR_PPF_SERIES', 'Charcoal Black Color PPF Series'),
    ]

    WARRANTY_YEARS_MAP = {
        'PREMIUM_MATTE_SERIES': 5,
        'PREMIUM_GLOSS_SERIES': 5,
        'TITANIUM_GLOSS_SERIES': 10,   # ✅ 10 Years
        'PIANO_BLACK_COLOR_PPF_SERIES': 5,
        'CHARCOAL_BLACK_COLOR_PPF_SERIES': 5,
    }

    APPROVAL_STATUS_CHOICES = [
        ('NOT_APPROVED', 'Not Approved'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    # ===================== PRIMARY KEY =====================
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ===================== CUSTOMER INFORMATION =====================
    customer_name = models.CharField(max_length=100, default='')
    email = models.EmailField()
    phone_number = models.CharField(max_length=15, default='')
    city = models.CharField(max_length=100, default='')
    state = models.CharField(max_length=100, default='')

    # ===================== VEHICLE INFORMATION =====================
    car_make_model = models.CharField(max_length=15, default='')
    vin_chassis_number = models.CharField(max_length=50, default='')
    installation_date = models.DateField(null=True, blank=True)

    # ===================== PPF DETAILS =====================
    ppf_variant = models.CharField(
        max_length=100,
        choices=PPF_VARIANT_CHOICES,
        default=''
    )

    installer_studio_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        default=''
    )

    # ===================== FILE UPLOADS =====================
    rc_upload = models.FileField(upload_to='warranty/rc/', default='')
    car_with_ppf_roll_box = models.ImageField(upload_to='warranty/car_images/', default='')

    # ===================== ADDITIONAL NOTES =====================
    special_notes = models.TextField(blank=True, null=True)

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

    # ===================== WARRANTY DETAILS =====================
    warranty_start_date = models.DateField(null=True, blank=True)
    warranty_end_date = models.DateField(null=True, blank=True)

    warranty_code = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )

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
        years = self.WARRANTY_YEARS_MAP.get(self.ppf_variant, 0)
        self.warranty_start_date = date.today()
        self.warranty_end_date = date.today() + relativedelta(years=years)
        self.warranty_code = self.generate_warranty_code()

    def __str__(self):
        return f"{self.customer_name} - {self.car_make_model}"





class ContactEnquiry(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ================= PERSONAL DETAILS =================
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)

    # ================= MESSAGE =================
    subject = models.CharField(max_length=200)
    message = models.TextField()

    attachment = models.FileField(
        upload_to="contact/attachments/",
        null=True,
        blank=True
    )

    # ================= CONSENT =================
    consent = models.BooleanField(default=False)

    # ================= SYSTEM =================
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.subject}"
