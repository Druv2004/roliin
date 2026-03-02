from rest_framework import serializers
from apps.accounts.models import Account
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = Account
        fields = ['id', 'email', 'username', 'password']

    def create(self, validated_data):
        user = Account.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField()
    
    
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value
    
    
class LogoutRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class LogoutResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    
    
class AdminCreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = Account
        fields = ["id", "email", "username", "password", "role", "is_active"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        role = validated_data.pop("role", "STAFF")
        password = validated_data.pop("password")

        user = Account.objects.create_user(**validated_data)
        user.set_password(password)
        user.role = role

        # optional: map role -> staff/superuser flags
        if role == "ADMIN":
            user.is_staff = True
            user.is_superuser = True
        else:
            user.is_staff = False
            user.is_superuser = False

        user.save()
        return user


class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "email", "username", "role", "is_active", "date_joined", "last_login"]