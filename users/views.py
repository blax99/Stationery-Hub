import logging
from urllib.parse import urlencode

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMultiAlternatives, send_mail
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.template.loader import render_to_string
from django.views.generic import TemplateView
from django.urls import reverse
from .serializers import RegisterSerializer, ProfileSerializer
from .permissions import IsAdmin, has_admin_access
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView

logger = logging.getLogger(__name__)


class LoginPageView(TemplateView):
    template_name = "users/login.html"


class LoginAPIView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.data.get("admin_only") and not has_admin_access(serializer.user):
            return Response(
                {"detail": "This account does not have admin access."},
                status=status.HTTP_403_FORBIDDEN,
            )
        auth_login(request._request, serializer.user)
        response = Response(serializer.validated_data, status=status.HTTP_200_OK)
        response.data["role"] = (
            "admin" if serializer.user.is_superuser else serializer.user.role
        )
        return response


@require_POST
def logout_view(request):
    auth_logout(request)
    return JsonResponse({"success": True})


class ForgotPasswordPageView(TemplateView):
    template_name = "users/forgot-password.html"


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        try:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verify_link = (
                f"{settings.SITE_URL}/users/verify-email/?uid={uid}&token={token}"
            )
            send_mail(
                subject="Verify your email - Stationery Hub",
                message=f"Click the link to verify your email: {verify_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
        except Exception:
            logger.exception("Failed to send registration email for user %s", user.pk)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "If this email exists, a reset link has been sent."},
                status=status.HTTP_200_OK,
            )

        try:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            site_url = (
                settings.SITE_URL or request.build_absolute_uri("/")
            ).rstrip("/")
            reset_url = f"{site_url}{reverse('password-reset-confirm')}"
            reset_link = f"{reset_url}?{urlencode({'uid': uid, 'token': token})}"
            context = {
                "username": user.get_short_name() or user.username,
                "reset_link": reset_link,
                "site_url": site_url,
            }
            text_message = (
                f"Hello {context['username']},\n\n"
                "We received a request to reset your Stationery Hub password. "
                f"Use this link to choose a new password:\n{reset_link}\n\n"
                "If you did not request this, you can safely ignore this email."
            )
            email = EmailMultiAlternatives(
                subject="Reset your Stationery Hub password",
                body=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            email.attach_alternative(
                render_to_string(
                    "users/emails/password_reset.html",
                    context,
                ),
                "text/html",
            )
            email.send()
        except Exception:
            logger.exception("Failed to send password reset email for user %s", user.pk)

        return Response(
            {"detail": "If this email exists, a reset link has been sent."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        uid = request.query_params.get("uid", "")
        token = request.query_params.get("token", "")

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (User.DoesNotExist, ValueError, TypeError):
            user = None

        token_is_valid = bool(
            user and default_token_generator.check_token(user, token)
        )
        return render(
            request,
            "users/password-reset-confirm.html",
            {
                "uid": uid,
                "token": token,
                "token_is_valid": token_is_valid,
            },
        )

    def post(self, request):
        uid = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response(
                {"detail": "Invalid link."}, status=status.HTTP_400_BAD_REQUEST
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(new_password, str) or not new_password:
            return Response(
                {"detail": "Enter a new password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(new_password, user)
        except ValidationError as error:
            return Response(
                {"detail": error.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"detail": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )


class RegisterPageView(TemplateView):
    template_name = "users/register.html"


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self):
        return self.request.user


class ProfilePageView(TemplateView):
    template_name = "users/profile.html"


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        uid = request.GET.get("uid")
        token = request.GET.get("token")

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response(
                {"detail": "Invalid verification link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_email_verified = True
        user.save()

        return Response(
            {"detail": "Email verified successfully."}, status=status.HTTP_200_OK
        )


class AdminUserListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAdmin]
    queryset = User.objects.all()
