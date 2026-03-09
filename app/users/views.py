from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
import random
from django.core.mail import send_mail
from rest_framework import status
from .models import PasswordResetCode
from .serializers import *
from app.users.models import User, TelegramLinkCode
from app.users.serializers import RegisterSerializers, UserProfileSerializers, TokenObtainPairSerializer

class RegisterAPI(mixins.CreateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializers

class ProfileAPI(mixins.RetrieveModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializers
    permission_classes = [IsAuthenticated,]

class TelegramLinkCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        obj, _ = TelegramLinkCode.objects.get_or_create(user=request.user)

        obj.code = TelegramLinkCode.generate_code()
        obj.is_user = False
        obj.save(update_fields=["code", "is_user"])

        return Response({"code": obj.code})

class CustomToken(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer



class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                code = str(random.randint(100000, 999999))
                PasswordResetCode.objects.create(user=user, code=code)

                send_mail(
                    'Сброс пароля',
                    f'Ваш код подтверждения: {code}',
                    'noreply@test.com',
                    [email],
                )
            return Response({"message": "Если email существует, код отправлен."}, status=200)
        return Response(serializer.errors, status=400)

class VerifyCodeView(APIView):
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            
            reset_entry = PasswordResetCode.objects.filter(
                user__email=email, code=code
            ).last()
            
            if reset_entry and reset_entry.is_valid():
                return Response({"message": "Код подтвержден. Можете менять пароль."}, status=200)
            return Response({"error": "Неверный или истекший код."}, status=400)
        return Response(serializer.errors, status=400)

class SetNewPasswordView(APIView):
    def post(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            new_password = serializer.validated_data['new_password']
            
            reset_entry = PasswordResetCode.objects.filter(
                user__email=email, code=code
            ).last()
            
            if reset_entry and reset_entry.is_valid():
                user = reset_entry.user
                user.set_password(new_password)
                user.save()
                reset_entry.delete()
                return Response({"message": "Пароль успешно изменен."}, status=200)
            return Response({"error": "Ошибка валидации кода."}, status=400)
        return Response(serializer.errors, status=400)