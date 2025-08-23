from django.utils import timezone
import datetime

from django.contrib.auth import user_login_failed, authenticate
from django.core.mail import send_mail
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .services import *
from .serializers import *
from django.conf import settings


class UserRegisterView(APIView):
    @swagger_auto_schema(
        operation_description="Register a new user account",
        request_body=UserRegisterSerializer,
        responses={
            201: openapi.Response(
                description="User created successfully",
                examples={
                    "application/json": {
                        "username": "newuser",
                        "email": "user@example.com",
                        "password": "••••••••"  # Password will be hashed and not returned in actual response
                    }
                }
            ),
            400: "Bad request - validation errors"
        }
    )
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    @swagger_auto_schema(
        operation_description="Authenticate user with email and password",
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "user_id": 1,
                        "email": "user@example.com",
                        "username": "username"
                    }
                }
            ),
            200: openapi.Response(
                description="2FA enabled - OTP code sent",
                examples={
                    "application/json": {
                        "user_id": 1
                    }
                }
            ),
            400: "Invalid credentials",
            404: "User not found"
        }
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = authenticate(
                request=request,
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
            )
            if user:
                if user.is_2fa_enabled:
                    otp_code = generateOTP()
                    user.otp = otp_code
                    user.otp_created_at = timezone.now()
                    user.save()
                    user_email = user.email

                    send_mail(
                        subject='Code',
                        message=f'Your OTP code is {otp_code}',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user_email],
                        fail_silently=False,
                    )

                    data = {
                        'user_id':user.id,
                    }
                    return Response(data, status=status.HTTP_200_OK)
                else:
                    refresh = RefreshToken.for_user(user)
                    return Response(
                        {
                            'refresh':str(refresh),
                            'access':str(refresh.access_token),
                            'user_id':user.id,
                            'email':user.email,
                            'username':user.username
                        }, status=status.HTTP_200_OK
                    )
            return Response({'error':'User not found'},status=status.HTTP_404_NOT_FOUND)
        return Response({'error':'Not valid credentials'},status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Logout the current user by blacklisting their JWT token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='JWT refresh token to blacklist'
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Successfully logged out",
                examples={
                    "application/json": {
                        "detail": "Successfully logged out."
                    }
                }
            ),
            401: "Authentication credentials not provided"
        },
        security=[{"Bearer": []}]
    )
    def post(self, request):
        # Blacklist the token
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    @swagger_auto_schema(
        operation_description="Get the authenticated user's profile information",
        responses={
            200: UserProfileSerializer,
            401: "Authentication credentials not provided"
        },
        security=[{"Bearer": []}]
    )

    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)


class UserOTPVerificationView(APIView):
    @swagger_auto_schema(
        operation_description="Verify OTP code for two-factor authentication",
        request_body=UserOTPVerificationSerializer,
        responses={
            200: openapi.Response(
                description="OTP verification successful",
                examples={
                    "application/json": {
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "user_id": 1,
                        "email": "user@example.com",
                        "username": "username"
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request",
                examples={
                    "application/json": {
                        "error": "invalid OTP code"
                    }
                }
            ),
            404: openapi.Response(
                description="User not found",
                examples={
                    "application/json": {
                        "error": "User not found"
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = UserOTPVerificationSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user_id = serializer.validated_data['user_id']
            entered_otp = serializer.validated_data['otp_code']

            try:
                user = MyUser.objects.get(id=user_id)
            except:
                return Response({'error':'User not found'}, status=status.HTTP_404_NOT_FOUND)

            otp_expiry_minutes = 3
            user_otp = user.otp
            current_time = timezone.now()

            if user.otp_created_at and (current_time - user.otp_created_at).total_seconds() > (otp_expiry_minutes * 60):
                user.otp = None
                user.otp_created_at = None
                user.save()
                return Response({'error':'OTP code has expired. Send a new one'}, status=status.HTTP_400_BAD_REQUEST)


            if not verifyOTP(entered_otp, user_otp):
                return Response({'error':'invalid OTP code'},status=status.HTTP_400_BAD_REQUEST)
            user.otp = None
            user.save()

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    'refresh':str(refresh),
                    'access':str(refresh.access_token),
                    'user_id':user_id,
                    'email':user.email,
                    'username':user.username
                }, status=status.HTTP_200_OK
            )
        return Response({'error':'Invalid information provided'}, status=status.HTTP_400_BAD_REQUEST)
