# import uuid
# from django.db import models
# from datetime import date
# from dateutil.relativedelta import relativedelta
# from django.conf import settings

# from django.contrib.auth.models import AbstractUser


# # ================================ ACCOUNTS MODELS ==================================
# class Account(AbstractUser):
#     email = models.EmailField(unique=True)

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username']

#     def __str__(self):
#         return self.email




# # ================================ WARRANTY MODELS ==================================
# class Warranty(models.Model):

#     PPF_CATEGORY_CHOICES = [
#         ('GLOSS_6', 'Gloss PPF – 6 Years'),
#         ('GLOSS_10', 'Gloss PPF – 10 Years'),
#         ('MATTE_6', 'Matte PPF – 6 Years'),
#         ('BLACK_6', 'Black PPF – 6 Years'),
#     ]

#     WARRANTY_YEARS_MAP = {
#         'GLOSS_6': 6,
#         'GLOSS_10': 10,
#         'MATTE_6': 6,
#         'BLACK_6': 6,
#     }

#     APPROVAL_STATUS_CHOICES = [
#         ('NOT_APPROVED', 'Not Approved'),
#         ('APPROVED', 'Approved'),
#         ('REJECTED', 'Rejected'),
#     ]

#     # Customer & Vehicle
#     customer_name = models.CharField(max_length=100)
#     phone_number = models.CharField(max_length=15)
#     email = models.EmailField()
#     car_number = models.CharField(max_length=20)
#     chassis_number = models.CharField(max_length=50)
#     camio_roll_unique_code = models.CharField(max_length=100, unique=True)

#     # PPF
#     ppf_category = models.CharField(max_length=20, choices=PPF_CATEGORY_CHOICES)

#     # Approval
#     approval_status = models.CharField(
#         max_length=20,
#         choices=APPROVAL_STATUS_CHOICES,
#         default='NOT_APPROVED'
#     )

#     approved_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True
#     )
#     approved_at = models.DateField(null=True, blank=True)

#     # Warranty dates
#     warranty_start_date = models.DateField(null=True, blank=True)
#     warranty_end_date = models.DateField(null=True, blank=True)

#     # 🔐 WARRANTY CODE (created after approval)
#     warranty_code = models.CharField(
#         max_length=50,
#         unique=True,
#         null=True,
#         blank=True
#     )

#     # Uploads
#     car_image_with_ppf = models.ImageField(upload_to='warranty/car_images/')
#     rc_photo = models.ImageField(upload_to='warranty/rc_photos/')

#     detailer_studio_name = models.CharField(max_length=150)
#     detailer_mobile_number = models.CharField(max_length=15)
#     location = models.CharField(max_length=150)

#     message = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     # 🔧 Warranty helpers
#     def generate_warranty_code(self):
#         today = date.today()
#         year = today.year
#         month = f"{today.month:02d}"

#         # Count approved warranties this month
#         count = Warranty.objects.filter(
#             approval_status='APPROVED',
#             approved_at__year=year,
#             approved_at__month=today.month
#         ).count() + 1

#         random_code = uuid.uuid4().hex[:4].upper()

#         return f"WR-{year}-{month}-{count:04d}-{random_code}"

#     def start_warranty(self):
#         years = self.WARRANTY_YEARS_MAP.get(self.ppf_category, 0)
#         self.warranty_start_date = date.today()
#         self.warranty_end_date = date.today() + relativedelta(years=years)
#         self.warranty_code = self.generate_warranty_code()

#     def __str__(self):
#         return f"{self.customer_name} - {self.car_number}"
