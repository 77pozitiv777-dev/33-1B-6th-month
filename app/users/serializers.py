from rest_framework import serializers
from app.users.models import User

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class RegisterSerializers(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name',
            'last_name',
            'created_at', 'password'
        ]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserProfileSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name',
            'last_name', 'is_active', 'is_staff', 
            'created_at'
        ]

class TokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod 
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        return token
        
    def validate(self, attrs):
        data = super().validate(attrs)
        data["role "] = self.user.role
        data["user_id"] = self.user.id
        data["email"] = self.user.email
        return data

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

class SetNewPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8, write_only=True)