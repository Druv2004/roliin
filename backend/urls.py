from rest_framework.routers import DefaultRouter
from apps.warranty.views import WarrantyViewSet, ContactViewSet
from apps.accounts.views import AuthViewSet

router = DefaultRouter()
router.register(r'warranty', WarrantyViewSet, basename='warranty')
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r"contact", ContactViewSet, basename="contact")

urlpatterns = router.urls
