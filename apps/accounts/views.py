from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from apps.accounts.models import Account
from apps.accounts.serializers import RegisterSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, ChangePasswordSerializer,LogoutRequestSerializer, LogoutResponseSerializer, AdminCreateUserSerializer, AdminUserListSerializer
import random
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.permissions import IsAdminUser




class AuthViewSet(viewsets.ViewSet):
    """
    JWT Authentication ViewSet (Login & Logout)
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Auth"],
        summary="Login",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "email": {"type": "string"},
                    "password": {"type": "string"}
                },
                "required": ["email", "password"]
            }
        }
    )
    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, email=email, password=password)

        if not user:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })
        
        
        
        
        
        
    @extend_schema(
        tags=["Auth"],
        summary="Logout",
        description="Logout user (client-side token removal)",
        responses={200: {"message": "Logout successful"}}
    )
    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def logout(self, request):
        refresh_token = request.data.get("refresh")

        # Try blacklist if refresh provided
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass  # ignore invalid refresh

        return Response(
            {"message": "Logout successful"},
            status=status.HTTP_200_OK
        )

    # 🔹 FORGOT PASSWORD (SEND CODE)
    @extend_schema(
        tags=["Auth"],
        summary="Forgot Password",
        request=ForgotPasswordSerializer,
        responses={200: {"message": "Reset code sent to email"}}
    )
    @action(detail=False, methods=['post'])
    def forgot_password(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return Response({"error": "Email is wrong"}, status=400)

        code = str(random.randint(100000, 999999))
        user.reset_code = code
        user.save(update_fields=['reset_code'])

        send_mail(
            subject="Password Reset Code",
            message=f"Your password reset code is {code}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return Response({"message": "Reset code sent to email"})


    # 🔹 RESET PASSWORD
    @extend_schema(
        tags=["Auth"],
        summary="Reset Password",
        request=ResetPasswordSerializer,
        responses={200: {"message": "Password reset successful"}}
    )
    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['new_password']

        try:
            user = Account.objects.get(email=email, reset_code=code)
        except Account.DoesNotExist:
            return Response({"error": "Invalid email or code"}, status=400)

        user.set_password(new_password)
        user.reset_code = None
        user.save()

        return Response({"message": "Password reset successful"})
    
    
    
    # 🔹 CHANGE PASSWORD
    @extend_schema(
        tags=["Auth"],
        summary="Change Password",
        description="Change password for logged-in user",
        request=ChangePasswordSerializer,
        responses={200: {"message": "Password changed successfully"}}
    )
    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        if not user.check_password(old_password):
            return Response(
                {"error": "Old password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password changed successfully"},
            status=status.HTTP_200_OK
        )
        
        
        
     # ✅ ADMIN: CREATE USER
    @action(detail=False, methods=["post"], permission_classes=[IsAdminUser])
    def create_user(self, request):
        serializer = AdminCreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"message": "User created successfully", "data": AdminUserListSerializer(user).data},
            status=status.HTTP_201_CREATED
        )

    # ✅ ADMIN: LIST USERS
    @action(detail=False, methods=["get"], permission_classes=[IsAdminUser])
    def users(self, request):
        qs = Account.objects.all().order_by("-date_joined")
        return Response(AdminUserListSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    # ✅ ADMIN: DELETE USER
    @action(detail=False, methods=["delete"], permission_classes=[IsAdminUser], url_path=r"users/(?P<user_id>[^/.]+)")
    def delete_user(self, request, user_id=None):
        # prevent deleting yourself (recommended)
        if str(request.user.id) == str(user_id):
            return Response({"error": "You cannot delete your own account."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Account.objects.get(id=user_id)
        except Account.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)

